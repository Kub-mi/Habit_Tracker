from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class Habit(models.Model):
    """
    Модель привычки согласно ТЗ.

    Полезная привычка (is_pleasant=False):
      - можно указать либо reward, либо linked_habit (но не оба сразу)
      - linked_habit (если указана) ДОЛЖНА быть 'приятной' (is_pleasant=True)

    Приятная привычка (is_pleasant=True):
      - НЕ может иметь reward
      - НЕ может иметь linked_habit
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name="Пользователь",
    )

    place = models.CharField("Место", max_length=255)
    time = models.TimeField("Время")
    action = models.CharField("Действие", max_length=255)

    is_pleasant = models.BooleanField(
        "Признак приятной привычки",
        default=False,
        help_text="Если включено — это приятная (вознаграждающая) привычка.",
    )

    linked_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dependent_habits",
        verbose_name="Связанная привычка",
        help_text="Должна ссылаться на ПРИЯТНУЮ привычку. "
                  "Используется для полезных привычек.",
    )

    periodicity_days = models.PositiveSmallIntegerField(
        "Периодичность (дней)",
        default=1,
        help_text="От 1 до 7 дней. Нельзя реже, чем раз в 7 дней.",
    )

    reward = models.CharField(
        "Вознаграждение",
        max_length=255,
        null=True,
        blank=True,
        help_text="Текстовое вознаграждение. "
                  "Не заполняется, если указана связанная приятная привычка.",
    )

    duration_sec = models.PositiveSmallIntegerField(
        "Время на выполнение (сек)",
        default=60, help_text="Не более 120 секунд."
    )

    is_public = models.BooleanField(
        "Публичная",
        default=False,
        help_text="Если включено — привычка видна в общем списке.",
    )

    created_at = models.DateTimeField("Создана", auto_now_add=True)

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ("-created_at",)
        # Минимальные check-констрейнты, которые можно выразить на уровне БД
        constraints = [
            models.CheckConstraint(
                check=Q(duration_sec__lte=120),
                name="habit_duration_le_120",
            ),
            models.CheckConstraint(
                check=Q(periodicity_days__gte=1) & Q(periodicity_days__lte=7),
                name="habit_periodicity_between_1_and_7",
            ),
        ]

    def clean(self):
        """
        Бизнес-валидация согласно ТЗ.
        Выполняется из сериализатора и из админки.
        """
        # 1) 0 < duration_sec <= 120
        if self.duration_sec is None or self.duration_sec > 120:
            raise ValidationError(
                {"duration_sec": "Время выполнения должно быть "
                                 "не больше 120 секунд."}
            )

        # 2) 1 <= periodicity_days <= 7
        if self.periodicity_days is None or not (1 <= self.periodicity_days <= 7):
            raise ValidationError(
                {
                    "periodicity_days": "Нельзя выполнять привычку реже, чем 1 раз в 7 дней."
                }
            )

        # Нормализуем reward для удобства проверок
        reward_filled = bool(self.reward and str(self.reward).strip())

        # 3) Приятная привычка: не может иметь reward или linked_habit
        if self.is_pleasant:
            if reward_filled:
                raise ValidationError(
                    {"reward": "У приятной привычки не может быть вознаграждения."}
                )
            if self.linked_habit is not None:
                raise ValidationError(
                    {
                        "linked_habit": "У приятной привычки не может быть связанной привычки."
                    }
                )

        # 4) Полезная привычка: нельзя одновременно и reward, и linked_habit
        if not self.is_pleasant:
            if reward_filled and self.linked_habit is not None:
                raise ValidationError(
                    "Нельзя одновременно указывать вознаграждение и связанную привычку."
                )

        # 5) В связанные могут попадать только 'приятные' привычки
        if self.linked_habit is not None and not self.linked_habit.is_pleasant:
            raise ValidationError(
                {
                    "linked_habit": "В связанные могут попадать только привычки с признаком 'приятной'."
                }
            )

        # 6) Запрет на самоссылку
        if self.pk and self.linked_habit_id == self.pk:
            raise ValidationError(
                {"linked_habit": "Нельзя связывать привычку саму с собой."}
            )

    def __str__(self):
        kind = "приятная" if self.is_pleasant else "полезная"
        return f"[{kind}] {self.action} @ {self.time} ({self.place})"
