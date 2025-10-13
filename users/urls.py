from django.urls import path

from .views import TelegramLinkView

urlpatterns = [
    path("me/telegram/", TelegramLinkView.as_view(), name="me-telegram"),
]
