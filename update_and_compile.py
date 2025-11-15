#!/usr/bin/env python
"""Обновление и компиляция переводов."""
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
    print("Обновление и компиляция переводов")
    print("=" * 60)
    
    # Шаг 1: Обновление файлов переводов
    print("\n[1/2] Обновление файлов переводов...")
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
    
    # Шаг 2: Компиляция через polib
    print("\n[2/2] Компиляция через polib...")
    try:
        import polib
        locale_dir = script_dir / 'locale'
        
        for lang in ['en', 'uz']:
            po_file = locale_dir / lang / 'LC_MESSAGES' / 'django.po'
            mo_file = locale_dir / lang / 'LC_MESSAGES' / 'django.mo'
            
            if po_file.exists():
                print(f"  Компиляция {lang}...")
                po = polib.pofile(str(po_file))
                mo_file.parent.mkdir(parents=True, exist_ok=True)
                po.save_as_mofile(str(mo_file))
                print(f"  ✓ {lang} скомпилирован ({len(po)} записей)")
        
        print("\n" + "=" * 60)
        print("✓ Все переводы успешно скомпилированы!")
        print("=" * 60)
    except ImportError:
        print("✗ polib не установлен. Установите: pip install polib")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

