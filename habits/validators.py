from django.core.exceptions import ValidationError


def validate_duration_le_120(duration_sec: int | None) -> None:
    if duration_sec is None or duration_sec > 120:
        raise ValidationError(
            {"duration_sec": "Время выполнения должно быть "
                             "не больше 120 секунд."}
        )


def validate_periodicity_in_1_7(days: int | None) -> None:
    if days is None or not (1 <= days <= 7):
        # Формулировка из ТЗ: нельзя реже, чем 1 раз в 7 дней
        raise ValidationError(
            {"periodicity_days": "Нельзя выполнять привычку реже, чем 1 раз в 7 дней."}
        )


def validate_reward_or_linked_exclusive(reward: str | None, linked) -> None:
    # Можно заполнить ТОЛЬКО одно из двух: reward ИЛИ linked_habit
    if (reward and str(reward).strip()) and linked is not None:
        raise ValidationError(
            "Нельзя одновременно указывать вознаграждение и связанную привычку."
        )


def validate_linked_is_pleasant(linked) -> None:
    # В связанные могут попадать только «приятные» привычки
    if linked is not None and not getattr(linked, "is_pleasant", False):
        raise ValidationError(
            {
                "linked_habit": "В связанные могут попадать только привычки с признаком приятной."
            }
        )


def validate_pleasant_has_no_reward_or_linked(
    is_pleasant: bool, reward: str | None, linked
) -> None:
    # У приятной НЕ может быть награды или связи
    if is_pleasant and ((reward and str(reward).strip()) or linked is not None):
        raise ValidationError(
            "У приятной привычки не может быть вознаграждения или связанной привычки."
        )


def validate_no_self_link(pk, linked_id) -> None:
    if pk and linked_id == pk:
        raise ValidationError(
            {"linked_habit": "Нельзя связывать привычку саму с собой."}
        )
