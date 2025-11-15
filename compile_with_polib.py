#!/usr/bin/env python
"""Компиляция переводов через polib (альтернатива msgfmt)."""
import os
import sys
from pathlib import Path

# Установка рабочей директории
script_dir = Path(__file__).resolve().parent
os.chdir(str(script_dir))

try:
    import polib
except ImportError:
    print("polib не установлен. Установите: pip install polib")
    sys.exit(1)

def compile_po_to_mo(po_file, mo_file):
    """Компилирует .po файл в .mo используя polib."""
    try:
        po = polib.pofile(str(po_file))
        po.save_as_mofile(str(mo_file))
        return True, None
    except Exception as e:
        return False, str(e)

if __name__ == '__main__':
    locale_dir = script_dir / 'locale'
    success = True
    
    print("=" * 60)
    print("Компиляция переводов через polib")
    print("=" * 60)
    
    for lang in ['en', 'uz']:
        po_file = locale_dir / lang / 'LC_MESSAGES' / 'django.po'
        mo_file = locale_dir / lang / 'LC_MESSAGES' / 'django.mo'
        
        if not po_file.exists():
            print(f"\n⚠ Файл {po_file} не найден, пропускаем")
            continue
        
        print(f"\nКомпиляция {lang}/LC_MESSAGES/django.po...")
        
        # Создаем директорию если нужно
        mo_file.parent.mkdir(parents=True, exist_ok=True)
        
        ok, error = compile_po_to_mo(po_file, mo_file)
        if ok:
            print(f"✓ {lang}/LC_MESSAGES/django.mo создан")
        else:
            print(f"✗ Ошибка при компиляции {lang}: {error}")
            success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✓ Все переводы успешно скомпилированы!")
    else:
        print("✗ Были ошибки при компиляции")
    print("=" * 60)
    
    sys.exit(0 if success else 1)

