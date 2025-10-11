# Habit Tracker Backend

REST API для отслеживания привычек, написанный на Django 5 и Django REST Framework. Проект
включает интеграцию с Telegram-ботом, асинхронные напоминания через Celery и Redis, JWT-аутентификацию и подробные проверки бизнес-логики.

## Ключевые возможности

- JWT-аутентификация (Djoser + SimpleJWT) и разграничение прав доступа для приватных и публичных привычек.
- Настроенный CORS c управлением списком доверенных доменов через переменные окружения.
- Telegram-интеграция: пользователи могут привязать chat_id, а Celery периодически отправляет напоминания о привычках.
- Пагинация списков привычек (5 элементов на страницу) и валидация бизнес-ограничений (вознаграждение, связанная привычка, периодичность, длительность).
- Покрытие тестами (Django TestCase + trace) не ниже 80%.

## Технологический стек

- Python 3.13
- Django 5.2, Django REST Framework
- PostgreSQL
- Celery + Redis
- Djoser, drf-spectacular, django-cors-headers
- Django TestCase, trace

## Переменные окружения

| Имя | Назначение |
| --- | --- |
| `SECRET_KEY` | Секретный ключ Django. |
| `DEBUG` | Включает режим отладки (`True`/`False`). |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Настройки подключения к PostgreSQL. |
| `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` | Подключение Celery к брокеру и хранилищу результатов (по умолчанию Redis). |
| `TELEGRAM_BOT_TOKEN` | Токен Telegram-бота для отправки сообщений. |
| `CORS_ALLOWED_ORIGINS` | Список разрешённых origin через запятую. |
| `CORS_ALLOW_ALL` | Разрешить все origin, если выставлено в `True`. |
| `CORS_ALLOW_CREDENTIALS` | Включить передачу cookie/заголовков авторизации. |
| `CORS_ALLOW_HEADERS` | Дополнительные разрешённые заголовки (через запятую). |

Файл `.env` не входит в репозиторий. Для локального запуска создайте его рядом с `manage.py` и заполните нужные значения.

## Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Celery-бит и воркер можно запустить командами:

```bash
celery -A config.celery worker -l info
celery -A config.celery beat -l info
```

## Тестирование и проверка стиля

```bash
python manage.py test
flake8
```

Для оценки покрытия можно использовать стандартный модуль `trace`:

```bash
python -m trace --count --coverdir=trace_cov manage.py test
python - <<'PY'
from pathlib import Path
modules = [
    "config.settings",
    "habits.models",
    "habits.views",
    "habits.serializers",
    "habits.tasks",
    "habits.permissions",
    "habits.pagination",
    "habits.validators",
    "telegramer.services",
    "users.models",
    "users.views",
    "users.serializers",
]
base = Path('trace_cov')
executed = total = 0
for mod in modules:
    path = base / f"{mod}.cover"
    if not path.exists():
        continue
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line or ':' not in line:
                continue
            count, _ = line.split(':', 1)
            count = count.strip()
            if not count or count.startswith('>>>>>>'):
                continue
            total += 1
            if count != '0':
                executed += 1
print(f"Coverage: {executed/total:.0%}" if total else "No modules measured")
PY
```

Файлы отчёта появятся в каталоге `trace_cov/`. Flake8 исключает директории миграций.

## Структура API

- `POST /api/v1/auth/jwt/create/` — получение пары токенов.
- `POST /api/v1/me/telegram/` — привязка Telegram chat_id.
- CRUD для привычек: `/api/v1/habits/` (требует авторизации).
- `GET /api/v1/habits/public/` — публичные привычки всех пользователей.
- `GET /api/docs/` — Swagger UI (drf-spectacular).

## Лицензия

Проект распространяется под лицензией MIT (если требуется, уточните при сдаче курсовой).