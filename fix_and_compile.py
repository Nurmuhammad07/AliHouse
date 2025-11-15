#!/usr/bin/env python
"""Исправление и компиляция переводов."""
import os
import sys
import django
from pathlib import Path

# Установка рабочей директории
script_dir = Path(__file__).resolve().parent
os.chdir(str(script_dir))

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, str(script_dir))

# Инициализация Django
django.setup()

from django.core.management import call_command

if __name__ == '__main__':
    print("=" * 60)
    print("Исправление и компиляция файлов переводов")
    print("=" * 60)
    
    # Шаг 1: Пересоздание файлов переводов
    print("\n[1/2] Обновление файлов переводов через makemessages...")
    try:
        call_command(
            'makemessages',
            '-l', 'en',
            '-l', 'uz',
            '--ignore=venv',
            '--ignore=.venv',
            '--ignore=env',
            '--no-obsolete',
            verbosity=1
        )
        print("✓ Файлы обновлены")
    except Exception as e:
        print(f"⚠ Предупреждение: {e}")
        print("Продолжаем компиляцию...")
    
    # Шаг 2: Компиляция с детальной проверкой
    print("\n[2/2] Компиляция файлов переводов...")
    
    # Сначала проверим файлы через msgfmt напрямую
    import subprocess
    locale_dir = script_dir / 'locale'
    errors_found = False
    
    for lang in ['en', 'uz']:
        po_file = locale_dir / lang / 'LC_MESSAGES' / 'django.po'
        if po_file.exists():
            print(f"\nПроверка {lang}/LC_MESSAGES/django.po...")
            try:
                # Попробуем использовать msgfmt для проверки
                result = subprocess.run(
                    ['msgfmt', '--check', '-o', '/dev/null', str(po_file)],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore'
                )
                if result.returncode != 0:
                    print(f"✗ Ошибка в файле {lang}:")
                    print(result.stderr)
                    errors_found = True
                else:
                    print(f"✓ Файл {lang} корректен")
            except FileNotFoundError:
                print(f"⚠ msgfmt не найден, пропускаем проверку для {lang}")
            except Exception as e:
                print(f"⚠ Ошибка при проверке {lang}: {e}")
    
    if errors_found:
        print("\n" + "=" * 60)
        print("✗ Найдены ошибки в файлах переводов!")
        print("=" * 60)
        print("\nПопробуйте исправить ошибки вручную или используйте:")
        print("  python manage.py makemessages -l en -l uz")
        sys.exit(1)
    
    # Теперь компилируем
    try:
        call_command('compilemessages', verbosity=2)
        print("\n" + "=" * 60)
        print("✓ Переводы успешно скомпилированы!")
        print("=" * 60)
    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ Ошибка при компиляции:")
        print("=" * 60)
        print(str(e))
        print("\nДетали ошибки:")
        import traceback
        traceback.print_exc()
        
        # Попробуем найти проблему через polib
        print("\n" + "=" * 60)
        print("Попытка найти проблему через polib...")
        print("=" * 60)
        try:
            import polib
            for lang in ['en', 'uz']:
                po_file = locale_dir / lang / 'LC_MESSAGES' / 'django.po'
                if po_file.exists():
                    try:
                        po = polib.pofile(str(po_file))
                        print(f"✓ Файл {lang} успешно загружен через polib ({len(po)} записей)")
                    except Exception as po_error:
                        print(f"✗ Ошибка в файле {lang}: {po_error}")
        except ImportError:
            print("polib не установлен. Установите: pip install polib")
        
        sys.exit(1)

