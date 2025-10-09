from rest_framework import serializers


class TelegramLinkSerializer(serializers.Serializer):
    chat_id = serializers.CharField(max_length=64)

    def validate_chat_id(self, v):
        v = v.strip()
        if not v or not v.lstrip("-").isdigit():
            raise serializers.ValidationError("Некорректный chat_id.")
        return v

    def save(self, **kwargs):
        user = self.context["request"].user
        profile = user.profile
        profile.telegram_chat_id = self.validated_data["chat_id"]
        profile.save(update_fields=["telegram_chat_id"])
        return profile
