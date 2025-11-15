import os
import sys
from pathlib import Path

# Установка рабочей директории
script_dir = Path(__file__).resolve().parent
os.chdir(str(script_dir))
sys.path.insert(0, str(script_dir))

# Импорт и выполнение
from create_po_files import EN_TRANSLATIONS, UZ_TRANSLATIONS, create_po_file, LOCALE_DIR

if __name__ == '__main__':
    en_path = LOCALE_DIR / "en" / "LC_MESSAGES" / "django.po"
    uz_path = LOCALE_DIR / "uz" / "LC_MESSAGES" / "django.po"
    
    create_po_file("en", EN_TRANSLATIONS, en_path)
    create_po_file("uz", UZ_TRANSLATIONS, uz_path)
    
    print(f"\n✓ Translation files created successfully!")
    print(f"  - {en_path}")
    print(f"  - {uz_path}")
    print(f"\nNext step: python manage.py compilemessages")

