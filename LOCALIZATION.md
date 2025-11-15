# Инструкция по локализации

## Генерация файлов переводов

После обновления всех шаблонов и форм с переводами, выполните следующие команды:

```bash
# Создать файлы переводов для английского и узбекского языков
python manage.py makemessages -l en -l uz --ignore=venv --ignore=.venv --ignore=env

# Или если используете Docker:
docker compose exec web python manage.py makemessages -l en -l uz --ignore=venv --ignore=.venv --ignore=env

# Или используйте скрипт generate_translations.py:
python generate_translations.py
```

Это создаст файлы:
- `locale/en/LC_MESSAGES/django.po`
- `locale/uz/LC_MESSAGES/django.po`

**Примечание:** Если у вас проблемы с кодировкой пути в PowerShell (например, путь содержит кириллицу) или отсутствуют GNU gettext tools, используйте скрипт `create_po_files.py`:

```bash
python create_po_files.py
```

Или выполните команду `makemessages` в Git Bash / WSL / Linux-окружении, где gettext tools установлены по умолчанию.

## Заполнение переводов

Откройте файлы `.po` и заполните переводы для всех строк. Пример:

```po
#: services/forms.py:9
msgid "Телефон"
msgstr "Phone"

#: services/forms.py:19
msgid "Пароль"
msgstr "Password"
```

Для узбекского языка:

```po
#: services/forms.py:9
msgid "Телефон"
msgstr "Telefon"

#: services/forms.py:19
msgid "Пароль"
msgstr "Parol"
```

## Компиляция переводов

После заполнения всех переводов, скомпилируйте их:

```bash
python manage.py compilemessages

# Или если используете Docker:
docker compose exec web python manage.py compilemessages
```

Это создаст файлы `.mo`, которые Django использует для переводов.

## Обновление переводов

Если вы добавили новые строки для перевода, выполните:

```bash
python manage.py makemessages -l en -l uz --ignore=venv --ignore=.venv --ignore=env
```

Затем заполните новые переводы и скомпилируйте:

```bash
python manage.py compilemessages
```

## Примечания

- Все строки в шаблонах должны быть обернуты в `{% trans "..." %}` или `{% blocktrans %}...{% endblocktrans %}`
- Все строки в Python коде должны использовать `gettext_lazy` или `gettext`
- После изменения переводов перезапустите сервер Django

