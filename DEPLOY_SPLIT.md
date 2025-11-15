# Раздельный деплой: Backend (Railway) + Frontend (Render)

Если вы хотите разделить деплой из-за ограничений бесплатного тарифа Railway, вот как это сделать.

## Вариант 1: Всё на Render (рекомендуется)

**Render предоставляет бесплатный тариф** для веб-сервисов и баз данных. Это самый простой вариант:

1. Задеплойте весь проект на Render (см. `DEPLOY.md`)
2. Используйте бесплатный PostgreSQL от Render
3. Всё работает в одном месте

**Преимущества:**
- ✅ Бесплатно
- ✅ Всё в одном месте
- ✅ Проще управлять

## Вариант 2: Раздельный деплой (если нужно)

Если вы всё же хотите разделить, вот как:

### Backend на Railway (API)

1. **Создайте проект на Railway**
2. **Добавьте PostgreSQL**
3. **Переменные окружения:**
   ```
   SECRET_KEY=<ваш-ключ>
   DEBUG=0
   ALLOWED_HOSTS=ваш-backend.railway.app,*.railway.app
   CSRF_TRUSTED_ORIGINS=https://ваш-backend.railway.app
   DATABASE_URL=<автоматически от Railway>
   ```

4. **Настройте CORS** (если фронтенд на другом домене):
   Добавьте в `requirements.txt`:
   ```
   django-cors-headers>=4.3
   ```
   
   В `core/settings.py`:
   ```python
   INSTALLED_APPS = [
       # ...
       "corsheaders",
   ]
   
   MIDDLEWARE = [
       "corsheaders.middleware.CorsMiddleware",  # Первым!
       # ... остальные
   ]
   
   CORS_ALLOWED_ORIGINS = [
       "https://ваш-фронтенд.onrender.com",
   ]
   ```

### Frontend на Render (веб-интерфейс)

1. **Создайте Web Service на Render**
2. **Подключите тот же репозиторий**
3. **Настройки:**
   - Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - Start: `gunicorn core.wsgi:application --bind 0.0.0.0:$PORT`

4. **Переменные окружения:**
   ```
   SECRET_KEY=<тот же ключ, что и на Railway>
   DEBUG=0
   ALLOWED_HOSTS=ваш-фронтенд.onrender.com,*.onrender.com
   CSRF_TRUSTED_ORIGINS=https://ваш-фронтенд.onrender.com
   DATABASE_URL=<URL от Railway PostgreSQL>
   ```

5. **Обновите шаблоны** для работы с API:
   Если нужно, обновите `templates/base.html` и другие шаблоны, чтобы они обращались к API на Railway вместо прямых запросов к Django.

## Вариант 3: Только Railway (бесплатный тариф)

Railway предоставляет **бесплатный Hobby план** с:
- $5 кредитов в месяц
- Достаточно для небольшого проекта
- Автоматическое засыпание после неактивности (но можно разбудить)

**Как использовать:**
1. Зарегистрируйтесь на Railway
2. Подключите GitHub
3. Создайте проект — первые $5 бесплатно каждый месяц
4. Для небольшого MVP этого обычно хватает

## Рекомендация

**Используйте Render для всего проекта** — это проще и бесплатно. Если нужен раздельный деплой, лучше делать это когда у вас действительно отдельный фронтенд (React/Vue) и отдельный API.

---

**Примечание:** Разделение Django-монолита на два сервиса не даёт особых преимуществ, так как это один и тот же код, работающий в двух местах. Это увеличивает сложность без реальной выгоды.

