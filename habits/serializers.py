from rest_framework import serializers

from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    # пользователь берётся из текущего запроса, не из входных данных
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Habit
        fields = (
            "id",
            "user",
            "place",
            "time",
            "action",
            "is_pleasant",
            "linked_habit",
            "periodicity_days",
            "reward",
            "duration_sec",
            "is_public",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def validate(self, attrs):
        """
        Вызовем бизнес-валидации модели. Создаём временный инстанс с
        учётом текущего контекста и дергаем .clean().
        """
        # собрать данные будущего объекта: учесть instance при update
        inst_data = {}
        if self.instance:
            # при partial_update отсутствие ключа значит «оставить как есть»
            for f in self.Meta.fields:
                if f in ("id", "created_at"):
                    continue
                if f in self.initial_data:
                    inst_data[f] = attrs.get(f, getattr(self.instance, f))
                else:
                    inst_data[f] = getattr(self.instance, f)
        else:
            # create
            inst_data = {**attrs}
            # user гарантирован HiddenField, но на всякий случай:
            if (
                "user" not in inst_data
                and self.context.get("request")
                and self.context["request"].user.is_authenticated
            ):
                inst_data["user"] = self.context["request"].user

        temp = Habit(**inst_data)
        # если это update — выставим pk, чтобы корректно
        # работала проверка самоссылки
        if self.instance:
            temp.pk = self.instance.pk

        # централизованные проверки модели
        temp.clean()

        return attrs
