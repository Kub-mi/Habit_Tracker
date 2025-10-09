import pytest
from django.urls import reverse

from habits.models import Habit


# pagination
@pytest.mark.django_db
def test_my_habits_pagination(jwt_user):
    client, user = jwt_user
    # создаём 11 привычек
    Habit.objects.bulk_create(
        [
            Habit(
                user=user,
                place="дом",
                time="08:00",
                action=f"a{i}",
                duration_sec=60,
                periodicity_days=1,
            )
            for i in range(11)
        ]
    )
    url = reverse("habit-list")  # /api/v1/habits/
    res = client.get(url + "?page=1")
    assert res.status_code == 200
    assert len(res.data["results"]) == 5
    assert res.data["count"] == 11
    assert res.data["next"] is not None


# pagination
@pytest.mark.django_db
def test_public_habits_pagination(api_client):  # api_client без токена
    # создаём 7 публичных привычек разных пользователей
    # тут можно через фабрики; ниже — псевдо
    from django.contrib.auth import get_user_model

    U = get_user_model()
    u = U.objects.create_user(email="x@test.com", password="pass12345")
    Habit.objects.bulk_create(
        [
            Habit(
                user=u,
                place="парк",
                time="21:00",
                action=f"p{i}",
                duration_sec=60,
                periodicity_days=1,
                is_public=True,
            )
            for i in range(7)
        ]
    )
    url = reverse("habit-public")  # кастомный action
    res = api_client.get(url + "?page=2")
    assert res.status_code == 200
    assert len(res.data["results"]) == 2  # 7 = 5 + 2


# permissions
@pytest.mark.django_db
def test_owner_can_update(jwt_user):
    client, user = jwt_user
    h = Habit.objects.create(
        user=user,
        place="дом",
        time="08:00",
        action="чай",
        duration_sec=60,
        periodicity_days=1,
    )
    url = reverse("habit-detail", args=[h.id])
    res = client.patch(url, {"action": "кофе"}, format="json")
    assert res.status_code == 200
    assert res.data["action"] == "кофе"


@pytest.mark.django_db
def test_other_user_cannot_update(jwt_user, user_factory):
    client, user = jwt_user
    other = user_factory(email="b@test.com")
    h = Habit.objects.create(
        user=other,
        place="дом",
        time="08:00",
        action="чай",
        duration_sec=60,
        periodicity_days=1,
    )
    url = reverse("habit-detail", args=[h.id])
    res = client.patch(url, {"action": "кофе"}, format="json")
    assert res.status_code in (
        403,
        404,
    )  # 403 из IsOwner, либо 404 если фильтруешь queryset


@pytest.mark.django_db
def test_public_list_is_open(api_client, user):
    Habit.objects.create(
        user=user,
        place="парк",
        time="21:00",
        action="прогулка",
        duration_sec=60,
        periodicity_days=1,
        is_public=True,
    )
    url = reverse("habit-public")
    res = api_client.get(url)
    assert res.status_code == 200
    assert res.data["count"] >= 1
