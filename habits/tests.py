from datetime import datetime, time, timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from habits import validators
from habits.models import Habit
from habits.tasks import send_habit_reminders


class HabitViewSetTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="owner",
            email="owner@example.com",
            password="pass12345",
        )
        self.client.force_authenticate(user=self.user)

    def test_my_habits_pagination(self):
        Habit.objects.bulk_create(
            [
                Habit(
                    user=self.user,
                    place="дом",
                    time=time(hour=8, minute=0),
                    action=f"a{i}",
                    duration_sec=60,
                    periodicity_days=1,
                )
                for i in range(11)
            ]
        )

        url = reverse("habit-list")
        response = self.client.get(url, {"page": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 5)
        self.assertEqual(response.data["count"], 11)
        self.assertIsNotNone(response.data["next"])

    def test_public_habits_pagination(self):
        other = get_user_model().objects.create_user(
            username="public-tester",
            email="public@example.com",
            password="pass12345",
        )
        Habit.objects.bulk_create(
            [
                Habit(
                    user=other,
                    place="парк",
                    time=time(hour=21, minute=0),
                    action=f"p{i}",
                    duration_sec=60,
                    periodicity_days=1,
                    is_public=True,
                )
                for i in range(7)
            ]
        )

        self.client.force_authenticate(user=None)
        url = reverse("habit-public")
        response = self.client.get(url, {"page": 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_owner_can_update(self):
        habit = Habit.objects.create(
            user=self.user,
            place="дом",
            time=time(hour=8, minute=0),
            action="чай",
            duration_sec=60,
            periodicity_days=1,
        )

        url = reverse("habit-detail", args=[habit.id])
        response = self.client.patch(url, {"action": "кофе"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["action"], "кофе")

    def test_other_user_cannot_update(self):
        other = get_user_model().objects.create_user(
            username="other",
            email="other@example.com",
            password="pass12345",
        )
        habit = Habit.objects.create(
            user=other,
            place="дом",
            time=time(hour=8, minute=0),
            action="чай",
            duration_sec=60,
            periodicity_days=1,
        )

        url = reverse("habit-detail", args=[habit.id])
        response = self.client.patch(url, {"action": "кофе"}, format="json")

        self.assertIn(response.status_code, {status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND})

    def test_public_list_is_open(self):
        Habit.objects.create(
            user=self.user,
            place="парк",
            time=time(hour=21, minute=0),
            action="прогулка",
            duration_sec=60,
            periodicity_days=1,
            is_public=True,
        )

        self.client.force_authenticate(user=None)
        url = reverse("habit-public")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["count"], 1)

    def test_send_habit_reminders(self):
        profile = self.user.profile
        profile.telegram_chat_id = "123456"
        profile.save(update_fields=["telegram_chat_id"])

        now = timezone.make_aware(datetime(2024, 1, 1, 9, 30))

        habit = Habit.objects.create(
            user=self.user,
            place="дом",
            time=now.time(),
            action="зарядка",
            duration_sec=60,
            periodicity_days=2,
        )

        Habit.objects.filter(pk=habit.pk).update(created_at=now - timedelta(days=2))
        habit.refresh_from_db()

        with patch("habits.tasks.timezone.localtime", return_value=now), patch(
            "habits.tasks.send_telegram_message"
        ) as fake_send:
            send_habit_reminders.run()

        fake_send.assert_called_once()
        args, _ = fake_send.call_args
        self.assertEqual(args[0], "123456")
        self.assertIn("зарядка", args[1])


class HabitValidatorTests(SimpleTestCase):
    def test_validate_duration_le_120(self):
        validators.validate_duration_le_120(120)
        with self.assertRaises(ValidationError):
            validators.validate_duration_le_120(121)

    def test_validate_periodicity_in_1_7(self):
        validators.validate_periodicity_in_1_7(1)
        with self.assertRaises(ValidationError):
            validators.validate_periodicity_in_1_7(0)

    def test_validate_reward_or_linked_exclusive(self):
        validators.validate_reward_or_linked_exclusive("", None)
        with self.assertRaises(ValidationError):
            validators.validate_reward_or_linked_exclusive("reward", object())

    def test_validate_linked_is_pleasant(self):
        class Dummy:
            is_pleasant = True

        validators.validate_linked_is_pleasant(Dummy())
        with self.assertRaises(ValidationError):
            validators.validate_linked_is_pleasant(object())

    def test_validate_pleasant_has_no_reward_or_linked(self):
        validators.validate_pleasant_has_no_reward_or_linked(False, "", None)
        with self.assertRaises(ValidationError):
            validators.validate_pleasant_has_no_reward_or_linked(True, "reward", None)

    def test_validate_no_self_link(self):
        validators.validate_no_self_link(1, 2)
        with self.assertRaises(ValidationError):
            validators.validate_no_self_link(1, 1)
