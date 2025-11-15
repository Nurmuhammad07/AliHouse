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
4. **После деплоя:** Railway → Deployments → View Logs → Terminal:
   ```bash
   python manage.py createsuperuser --phone +79990000000 --name "Admin"
   ```

## Минимальные шаги для Render

1. **Создайте Web Service:** New + → Web Service → Connect GitHub repo
2. **Настройки:**
   - Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - Start: `gunicorn core.wsgi:application --bind 0.0.0.0:$PORT`
3. **Создайте PostgreSQL:** New + → PostgreSQL
4. **Переменные окружения:**
   ```
   DATABASE_URL=<скопируйте из PostgreSQL сервиса>
   SECRET_KEY=<сгенерируйте>
   DEBUG=0
   ALLOWED_HOSTS=*.onrender.com
   CSRF_TRUSTED_ORIGINS=https://*.onrender.com
   ```
5. **После деплоя:** Shell → `python manage.py createsuperuser`

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

