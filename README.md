# AliHouse Service MVP

Минималистичный сервисный сайт на Django + DRF + PostgreSQL: каталог услуг, создание заявок, отслеживание статуса, личный кабинет и отзывы, плюс REST API и готовность к деплою на Railway/Render.

## Стек

- Django 5, DRF, кастомный пользователь с входом по телефону
- PostgreSQL (через `dj-database-url`) + SQLite fallback
- Gunicorn + Procfile/Dockerfile для PaaS
- Адаптивные шаблоны на чистом HTML/CSS

## Структура

- `core/` – базовые настройки проекта
- `services/` – доменная логика (модели, админка, API, формы, CRM-вьюхи)
- `services/crm_urls.py`, `templates/crm/` – веб-интерфейс CRM
- `templates/`, `static/` – минималистичный UI (включая светлую/тёмную темы)
- `api_urls.py` – DRF endpoints
- `env.example` – образец переменных окружения

## Быстрый старт (локально)

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
cp env.example .env.development  # шаблон
copy .env.development .env       # Windows
# Убедитесь, что SECRET_KEY заполнен, а для SQLite стоит USE_SQLITE=1
python manage.py migrate
python manage.py createsuperuser --phone +79990000000 --name "Admin"
python manage.py runserver
```

Доступы:

- Сайт: http://127.0.0.1:8000/
- Админка: http://127.0.0.1:8000/admin/

## Docker / Compose

```bash
docker compose up --build
```

Сервис поднимется на `http://localhost:8000`, Postgres доступен на `5432`.

## Ключевые переменные окружения

| Имя | Описание |
| --- | --- |
| `SECRET_KEY` | обязательный секрет Django (нет значения по умолчанию) |
| `DEBUG` | `1`/`0` |
| `DJANGO_ENV` | имя файла `.env.<name>` для override (`development`, `production`, …) |
| `ALLOWED_HOSTS` | список хостов через запятую |
| `CSRF_TRUSTED_ORIGINS` | список origin |
| `DATABASE_URL` | строка подключения Postgres/Cloud |
| `USE_SQLITE` | явно включите `1`, если хотите локальный SQLite |

Файл `env.example` — только шаблон. Он **не** подгружается автоматически: создайте `.env` и/или `.env.<environment>` вручную и настройте переменные (особенно `SECRET_KEY` и `DATABASE_URL`).

Без `DATABASE_URL` приложение не стартует, пока вы явно не выставите `USE_SQLITE=1`, чтобы избежать случайного запуска на SQLite в продакшене.

## API

Все запросы, кроме `/api/services/`, требуют аутентификацию (session или DRF token). Получить токен:

```bash
python manage.py drf_create_token <phone>
# или POST /api/auth/token/ с полями phone + password
```

Префикс `/api/`:

| Метод | Путь | Описание |
| --- | --- | --- |
| `POST` | `/api/auth/token/` | Получить DRF токен (phone + password) |
| `GET` | `/api/services/` | Список активных услуг (публично) |
| `POST` | `/api/orders/` | Создание заявки (автор берётся из токена) |
| `GET` | `/api/orders/<id>/` | Детали своей заявки |
| `POST` | `/api/feedback/` | Отзыв по своей завершённой заявке (`order`, `rating`, `text`) |
| `GET` | `/api/crm/orders/` | Список заявок (фильтры: `status`, `priority`, `operator`, `phone`) |
| `PATCH` | `/api/crm/orders/<id>/` | Изменение статуса/приоритета/оператора |
| `POST` | `/api/crm/orders/<id>/comments/` | Добавить внутренний комментарий |
| `GET` | `/api/crm/customers/` | Список клиентов (поиск `phone`) |
| `PATCH` | `/api/crm/customers/<id>/` | Обновление заметок по клиенту |

Для продакшена дополнительно стоит включить rate-limit/Throttling на уровне DRF или reverse proxy.

## Роли и CRM

- `admin` — полный доступ, может управлять пользователями/CRM.
- `operator` — доступ только к CRM (дашборд, заявки, клиенты, API).
- `user` — личный кабинет, создание заявок и отзывов.

Веб-CRM доступна по `/crm/` (дашборд, список заявок, карточки клиентов). Интерфейс минималистичный: фильтры по статусу/приоритету/оператору, управление назначениями, комментирование заказов, заметки по клиенту и адаптивные таблицы.

## Личный кабинет и UI

- Каталог услуг (`/`)
- Создание заявки (`/orders/new/`)
- История и статусы (`/dashboard/`)
- Детали заявки + отзыв (`/orders/<id>/`, `/feedback/<id>/`)
- Вход по телефону + пароль, регистрация

Все шаблоны находятся в `templates/`, стили — `static/css/app.css`.

## Деплой на Railway/Render

**📖 Подробная инструкция:** см. [DEPLOY.md](DEPLOY.md)

Кратко:
- `requirements.txt`, `Procfile`, `Dockerfile` готовы
- Настройте переменные окружения (`SECRET_KEY`, `DEBUG=0`, `DATABASE_URL`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`)
- Railway/Render автоматически применят миграции и соберут статику
- После деплоя создайте суперпользователя через терминал платформы

## Дополнительно

- Статусы заказов управляются через админку
- Отзыв доступен только после статуса `Завершена`
- Формы и API валидируют повторные отзывы и выключенные услуги

Готово к дальнейшему развитию: интеграция платежей, расширение личного кабинета, уведомления и т.д.

