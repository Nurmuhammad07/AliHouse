#!/usr/bin/env python
"""Временный скрипт для генерации файлов переводов."""
import os
import sys
import django

# Получить абсолютный путь к директории скрипта
script_dir = os.path.dirname(os.path.abspath(__file__))

# Изменить рабочую директорию
os.chdir(script_dir)

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, script_dir)

# Инициализация Django
django.setup()

# Теперь можно использовать Django management commands
from django.core.management import call_command

if __name__ == '__main__':
    try:
        print("Генерация файлов переводов...")
        call_command('makemessages', '-l', 'en', '-l', 'uz', '--ignore=venv', '--ignore=.venv', '--ignore=env')
        print("\nФайлы переводов успешно созданы!")
        print("Теперь нужно заполнить переводы в файлах:")
        print("  - locale/en/LC_MESSAGES/django.po")
        print("  - locale/uz/LC_MESSAGES/django.po")
        print("\nПосле заполнения выполните: python manage.py compilemessages")
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

