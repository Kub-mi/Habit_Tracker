from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TelegramLinkViewTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="user@example.com",
            password="pass12345",
        )
        self.url = reverse("me-telegram")

    def test_telegram_link_requires_auth(self):
        response = self.client.post(self.url, {"chat_id": "123"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_telegram_link_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {"chat_id": "987654"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.telegram_chat_id, "987654")
        self.assertEqual(response.data, {"ok": True, "chat_id": "987654"})

    def test_telegram_link_validation(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {"chat_id": "bad id"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Некорректный", str(response.data["chat_id"][0]))
