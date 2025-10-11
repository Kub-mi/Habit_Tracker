import os
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from telegramer import services


class TelegramServiceTests(SimpleTestCase):
    def tearDown(self):
        os.environ.pop("TELEGRAM_BOT_TOKEN", None)

    def test_get_bot_token_missing(self):
        with self.assertRaises(services.TelegramError):
            services.get_bot_token()

    def test_send_telegram_message_success(self):
        os.environ["TELEGRAM_BOT_TOKEN"] = "123:ABC"

        dummy_response = Mock()
        dummy_response.ok = True
        dummy_response.json.return_value = {"ok": True}

        with patch.object(services.requests, "post", return_value=dummy_response) as fake_post:
            result = services.send_telegram_message("111", "hi")

        fake_post.assert_called_once()
        args, kwargs = fake_post.call_args
        self.assertIn("123:ABC", args[0])
        self.assertEqual(kwargs["json"]["chat_id"], "111")
        self.assertEqual(result, {"ok": True})

    def test_send_telegram_message_error(self):
        os.environ["TELEGRAM_BOT_TOKEN"] = "123:ABC"

        dummy_response = Mock()
        dummy_response.ok = False
        dummy_response.status_code = 500
        dummy_response.text = "fail"

        with patch.object(services.requests, "post", return_value=dummy_response):
            with self.assertRaises(services.TelegramError) as exc:
                services.send_telegram_message("111", "hi")

        self.assertIn("Telegram send failed", str(exc.exception))