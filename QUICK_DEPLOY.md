# Быстрый деплой — шпаргалка

## Минимальные шаги для Railway

1. **Создайте проект:** New Project → Deploy from GitHub
2. **Добавьте PostgreSQL:** + New → Database → PostgreSQL
3. **Переменные окружения:**
   ```
   SECRET_KEY=<сгенерируйте через: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
   DEBUG=0
   ALLOWED_HOSTS=*.railway.app
   CSRF_TRUSTED_ORIGINS=https://*.railway.app
   ```
4. **Автоматическое создание админа (опционально):**
   Добавьте переменные:
   ```
   DJANGO_SUPERUSER_PHONE=+79990000000
   DJANGO_SUPERUSER_PASSWORD=ваш-пароль
   DJANGO_SUPERUSER_NAME=Admin
   ```
   Суперпользователь создастся автоматически при первом запуске.

## Минимальные шаги для Render

1. **Создайте Web Service:** New + → Web Service → Connect GitHub repo
2. **Настройки:**
   - Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - Start: `python manage.py migrate --noinput && gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --workers 2`
   - **Или:** Render автоматически использует `Procfile` (миграции уже включены)
   - **Суперпользователь:** создастся автоматически при первом запуске (если переменные установлены)
3. **Создайте PostgreSQL:** New + → PostgreSQL
4. **Переменные окружения:**
   ```
   DATABASE_URL=<скопируйте из PostgreSQL сервиса>
   SECRET_KEY=<сгенерируйте>
   DEBUG=0
   ALLOWED_HOSTS=*.onrender.com
   CSRF_TRUSTED_ORIGINS=https://*.onrender.com
   ```
5. **Автоматическое создание админа (опционально):**
   Добавьте переменные:
   ```
   DJANGO_SUPERUSER_PHONE=+79990000000
   DJANGO_SUPERUSER_PASSWORD=ваш-пароль
   DJANGO_SUPERUSER_NAME=Admin
   ```
   Суперпользователь создастся автоматически при первом запуске.

## Генерация SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Проверка после деплоя

- ✅ Главная страница открывается
- ✅ `/admin/` работает
- ✅ CSS/JS загружаются (F12 → Network)
- ✅ `/api/services/` возвращает JSON

---

Подробности: [DEPLOY.md](DEPLOY.md)

