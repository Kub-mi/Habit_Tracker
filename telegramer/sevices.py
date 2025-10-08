import os
import requests

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"

class TelegramError(RuntimeError):
    pass

def get_bot_token() -> str:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise TelegramError("TELEGRAM_BOT_TOKEN is not set")
    return token

def send_telegram_message(chat_id: str, text: str) -> dict:
    """
    Отправка простого текстового сообщения.
    """
    token = get_bot_token()
    url = TELEGRAM_API.format(token=token)
    resp = requests.post(url, json={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }, timeout=10)
    if not resp.ok:
        raise TelegramError(f"Telegram send failed: {resp.status_code} {resp.text}")
    return resp.json()