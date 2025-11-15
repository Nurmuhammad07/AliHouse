# PWA Setup Guide

Ваш проект теперь поддерживает PWA (Progressive Web App) функциональность!

## Что было добавлено:

1. **manifest.json** - манифест приложения с метаданными
2. **service-worker.js** - Service Worker для кеширования и офлайн-работы
3. **pwa.js** - скрипт регистрации PWA
4. **Meta теги** - добавлены в base.html и landing.html
5. **URL маршрут** - для service-worker.js

## Функции PWA:

✅ **Установка на устройство** - пользователи могут установить приложение как нативное
✅ **Офлайн-работа** - базовые страницы работают без интернета
✅ **Кеширование** - быстрая загрузка благодаря кешу
✅ **Обновления** - автоматическое уведомление о новых версиях
✅ **Иконки** - поддержка иконок для разных устройств

## Создание иконок:

### Вариант 1: Использовать скрипт (требует Pillow)

```bash
pip install Pillow
python generate_icons.py
```

Это создаст простые иконки с текстом "AH" на оранжевом фоне.

### Вариант 2: Создать вручную

Создайте иконки следующих размеров в `static/icons/`:
- icon-72x72.png
- icon-96x96.png
- icon-128x128.png
- icon-144x144.png
- icon-152x152.png
- icon-192x192.png
- icon-384x384.png
- icon-512x512.png

Рекомендуется использовать онлайн-генераторы:
- https://realfavicongenerator.net/
- https://www.pwabuilder.com/imageGenerator

## Тестирование PWA:

### Локально (HTTP):

1. Запустите сервер: `python manage.py runserver`
2. Откройте DevTools (F12) → Application → Service Workers
3. Проверьте регистрацию Service Worker
4. Проверьте Manifest в разделе Manifest

### В Production (HTTPS обязательно):

PWA требует HTTPS для работы в production. Убедитесь, что:
- Ваш сайт доступен по HTTPS
- SSL сертификат валиден
- Service Worker зарегистрирован

## Проверка PWA:

1. **Chrome DevTools:**
   - F12 → Application → Manifest
   - F12 → Application → Service Workers
   - F12 → Lighthouse → Run audit → PWA

2. **Мобильные устройства:**
   - Откройте сайт в браузере
   - Должна появиться кнопка "Установить приложение"
   - После установки приложение появится на главном экране

## Настройка:

### Изменить цвета темы:

В `static/manifest.json`:
```json
{
  "theme_color": "#ff6b35",  // Цвет темы
  "background_color": "#fdfdfd"  // Цвет фона
}
```

### Изменить название:

В `static/manifest.json`:
```json
{
  "name": "Ваше название",
  "short_name": "Короткое название"
}
```

## Важные замечания:

1. **HTTPS обязателен** для production (localhost работает с HTTP)
2. **Иконки обязательны** для полноценной работы PWA
3. **Service Worker** кеширует только GET запросы
4. **API запросы** не кешируются (они должны быть свежими)

## Обновление Service Worker:

При изменении `service-worker.js`:
1. Измените `CACHE_NAME` в файле
2. Service Worker автоматически обновится
3. Пользователи увидят уведомление об обновлении

## Troubleshooting:

**Service Worker не регистрируется:**
- Проверьте консоль браузера на ошибки
- Убедитесь, что файл доступен по `/static/service-worker.js`
- Проверьте HTTPS (для production)

**Иконки не отображаются:**
- Убедитесь, что файлы находятся в `static/icons/`
- Проверьте пути в `manifest.json`
- Выполните `python manage.py collectstatic`

**Приложение не устанавливается:**
- Проверьте, что все требования PWA выполнены (Lighthouse)
- Убедитесь, что используется HTTPS
- Проверьте manifest.json на ошибки

## Дополнительные ресурсы:

- [MDN: Progressive Web Apps](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [Web.dev: PWA](https://web.dev/progressive-web-apps/)
- [PWA Builder](https://www.pwabuilder.com/)

