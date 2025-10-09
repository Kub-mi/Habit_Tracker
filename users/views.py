from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import TelegramLinkSerializer


class TelegramLinkView(APIView):
    """
    POST /api/v1/me/telegram/
    { "chat_id": "123456789" }
    Привязывает chat_id к текущему пользователю.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = TelegramLinkSerializer(
            data=request.data,
            context={"request": request}
        )
        ser.is_valid(raise_exception=True)
        profile = ser.save()
        return Response(
            {"ok": True, "chat_id": profile.telegram_chat_id},
            status=status.HTTP_200_OK
        )
