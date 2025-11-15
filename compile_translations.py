#!/usr/bin/env python
"""Скрипт для компиляции переводов."""
import os
import sys
import django
from pathlib import Path

# Получить абсолютный путь к директории скрипта
script_dir = Path(__file__).resolve().parent

# Изменить рабочую директорию
os.chdir(str(script_dir))

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, str(script_dir))

# Инициализация Django
django.setup()

# Теперь можно использовать Django management commands
from django.core.management import call_command

if __name__ == '__main__':
    try:
        print("Проверка файлов переводов...")
        # Сначала попробуем пересоздать файлы, чтобы исправить возможные ошибки
        print("Обновление файлов переводов...")
        try:
            call_command('makemessages', '-l', 'en', '-l', 'uz', '--ignore=venv', '--ignore=.venv', '--ignore=env', verbosity=1)
            print("✓ Файлы обновлены")
        except Exception as e:
            print(f"Предупреждение при обновлении: {e}")
        
        print("\nКомпиляция файлов переводов...")
        call_command('compilemessages', verbosity=2)
        print("\n✓ Переводы успешно скомпилированы!")
    except Exception as e:
        print(f"\nОшибка: {e}")
        import traceback
        traceback.print_exc()
        
        # Попробуем найти конкретную ошибку
        print("\nПопытка найти проблемные файлы...")
        from pathlib import Path
        locale_dir = script_dir / 'locale'
        for lang in ['en', 'uz']:
            po_file = locale_dir / lang / 'LC_MESSAGES' / 'django.po'
            if po_file.exists():
                print(f"\nПроверка {po_file}...")
                try:
                    # Попробуем прочитать файл через polib если доступен
                    try:
                        import polib
                        po = polib.pofile(str(po_file))
                        print(f"  ✓ Файл {lang} корректен (проверено через polib)")
                    except ImportError:
                        print("  (polib не установлен, пропускаем проверку)")
                    except Exception as po_error:
                        print(f"  ✗ Ошибка в файле {lang}: {po_error}")
                except:
                    pass
        sys.exit(1)

