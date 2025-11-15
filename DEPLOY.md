# Инструкция по деплою AliHouse

Пошаговое руководство по развёртыванию проекта на Railway или Render.

## Подготовка

1. **Убедитесь, что код закоммичен в Git:**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Проверьте, что все миграции применены локально:**
   ```bash
   python manage.py migrate
   ```

## Деплой на Railway

### Шаг 1: Создание проекта

1. Зайдите на [railway.app](https://railway.app)
2. Войдите через GitHub
3. Нажмите "New Project" → "Deploy from GitHub repo"
4. Выберите репозиторий AliHouse

### Шаг 2: Настройка базы данных

1. В проекте нажмите "+ New" → "Database" → "Add PostgreSQL"
2. Railway автоматически создаст базу и добавит переменную `DATABASE_URL`

### Шаг 3: Настройка переменных окружения

В разделе "Variables" добавьте:

```
SECRET_KEY=ваш-случайный-секретный-ключ-минимум-50-символов
DEBUG=0
ALLOWED_HOSTS=ваш-домен.railway.app,*.railway.app
CSRF_TRUSTED_ORIGINS=https://ваш-домен.railway.app
DJANGO_ENV=production
```

**Как сгенерировать SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Шаг 4: Настройка деплоя

1. Railway автоматически определит `Procfile` или `Dockerfile`
2. Если используете Dockerfile, убедитесь что порт берётся из `$PORT` (Railway автоматически его устанавливает)
3. Нажмите "Deploy"

### Шаг 5: Первоначальная настройка

После успешного деплоя выполните в терминале Railway (или через CLI):

```bash
railway run python manage.py migrate
railway run python manage.py createsuperuser --phone +79990000000 --name "Admin"
```

### Шаг 6: Получение домена

1. В настройках проекта → "Settings" → "Generate Domain"
2. Скопируйте домен и обновите `ALLOWED_HOSTS` и `CSRF_TRUSTED_ORIGINS`

## Деплой на Render

### Шаг 1: Создание проекта

1. Зайдите на [render.com](https://render.com)
2. Войдите через GitHub
3. Нажмите "New +" → "Web Service"
4. Подключите репозиторий AliHouse

### Шаг 2: Настройка сервиса

- **Name:** `alihouse` (или любое другое)
- **Environment:** `Python 3`
- **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- **Start Command:** `gunicorn core.wsgi:application --bind 0.0.0.0:$PORT`

### Шаг 3: Настройка базы данных

1. "New +" → "PostgreSQL"
2. Создайте базу данных
3. Скопируйте "Internal Database URL"
4. В настройках Web Service добавьте переменную:
   - Key: `DATABASE_URL`
   - Value: скопированный URL

### Шаг 4: Переменные окружения

В разделе "Environment" добавьте:

```
SECRET_KEY=ваш-случайный-секретный-ключ
DEBUG=0
ALLOWED_HOSTS=ваш-домен.onrender.com
CSRF_TRUSTED_ORIGINS=https://ваш-домен.onrender.com
DJANGO_ENV=production
```

### Шаг 5: Деплой и миграции

1. Нажмите "Create Web Service"
2. После деплоя откройте "Shell" в Render Dashboard
3. Выполните:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser --phone +79990000000 --name "Admin"
   ```

## Проверка после деплоя

1. **Откройте сайт:** проверьте, что главная страница загружается
2. **Проверьте админку:** `/admin/` должна открываться
3. **Проверьте статику:** CSS/JS должны загружаться (F12 → Network)
4. **Проверьте API:** `/api/services/` должен возвращать JSON

## Решение проблем

### Статика не загружается

- Убедитесь, что `whitenoise` в `requirements.txt`
- Проверьте, что `collectstatic` выполняется при деплое
- В Render добавьте `collectstatic` в Build Command

### Ошибка "SECRET_KEY is not set"

- Проверьте переменные окружения в панели платформы
- Убедитесь, что переменная называется именно `SECRET_KEY`

### Ошибка подключения к БД

- Проверьте `DATABASE_URL` в переменных окружения
- Убедитесь, что база данных создана и запущена
- Для Railway: база должна быть в том же проекте

### 500 Internal Server Error

- Проверьте логи в панели платформы
- Убедитесь, что `DEBUG=0` в продакшене
- Проверьте, что миграции применены

### CSRF ошибки

- Добавьте домен в `CSRF_TRUSTED_ORIGINS` (с `https://`)
- Убедитесь, что `ALLOWED_HOSTS` содержит ваш домен

## Обновление после изменений

1. Закоммитьте изменения:
   ```bash
   git add .
   git commit -m "Update"
   git push
   ```

2. Платформа автоматически задеплоит изменения
3. Если нужно применить миграции:
   ```bash
   # Railway
   railway run python manage.py migrate
   
   # Render (через Shell)
   python manage.py migrate
   ```

## Рекомендации для продакшена

1. **Используйте PostgreSQL** (не SQLite)
2. **DEBUG=0** всегда в продакшене
3. **Настройте резервное копирование БД** (Railway/Render делают это автоматически)
4. **Мониторинг:** настройте алерты на ошибки
5. **Логи:** регулярно проверяйте логи приложения

## Дополнительные настройки

### Настройка домена (опционально)

1. **Railway:** Settings → Custom Domain
2. **Render:** Settings → Custom Domain
3. Обновите `ALLOWED_HOSTS` и `CSRF_TRUSTED_ORIGINS`

### Настройка SSL

Railway и Render автоматически предоставляют SSL-сертификаты для всех доменов.

---

Готово! Ваш проект должен быть доступен по адресу, который предоставит платформа.

