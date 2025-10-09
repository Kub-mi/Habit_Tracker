from celery import shared_task
from django.utils import timezone
from django.db.models import Q

from .models import Habit
from telegramer.services import send_telegram_message

@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def send_habit_reminders(self):
    """
    Раз в минуту отправляем напоминания по времени и периодичности.
    """
    now = timezone.localtime()
    today = now.date()

    # Берём только те привычки, у которых совпали час и минута
    qs = Habit.objects.filter(
        time__hour=now.hour,
        time__minute=now.minute,
    ).select_related("user__profile")

    for h in qs:
        # проверяем периодичность: раз в N дней, якорь — дата создания
        delta_days = (today - h.created_at.date()).days
        if delta_days < 0:
            continue
        if h.periodicity_days and (delta_days % h.periodicity_days != 0):
            continue

        profile = getattr(h.user, "profile", None)
        chat_id = getattr(profile, "telegram_chat_id", None)
        if not chat_id:
            continue  # пользователь не привязал Telegram

        text = (
            f"🔔 <b>Напоминание о привычке</b>\n"
            f"Действие: <b>{h.action}</b>\n"
            f"Место: {h.place}\n"
            f"Время на выполнение: {h.duration_sec} сек.\n"
            f"{'Публичная' if h.is_public else 'Приватная'}"
        )

        try:
            send_telegram_message(chat_id, text)
        except Exception as e:
            # Логируем и идём дальше; при желании можно self.retry()
            continue