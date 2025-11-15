#!/usr/bin/env python
"""Проверка файлов .po на синтаксические ошибки."""
import os
from pathlib import Path

def check_po_file(file_path):
    """Проверяет файл .po на синтаксические ошибки."""
    errors = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Пропускаем комментарии и пустые строки
        if not line or line.startswith('#'):
            i += 1
            continue
        
        # Проверяем msgid
        if line.startswith('msgid '):
            msgid_line = line
            i += 1
            # Проверяем многострочные msgid
            while i < len(lines) and lines[i].startswith('"'):
                msgid_line += '\n' + lines[i].strip()
                i += 1
            
            # Проверяем, что есть соответствующий msgstr
            if i >= len(lines):
                errors.append(f"Строка {i+1}: msgid без msgstr в конце файла")
                break
            
            # Пропускаем пустые строки
            while i < len(lines) and not lines[i].strip():
                i += 1
            
            if i >= len(lines) or not lines[i].strip().startswith('msgstr '):
                errors.append(f"Строка {i+1}: msgid без msgstr: {msgid_line[:50]}")
                continue
            
            # Проверяем msgstr
            msgstr_line = lines[i].strip()
            i += 1
            while i < len(lines) and lines[i].startswith('"'):
                msgstr_line += '\n' + lines[i].strip()
                i += 1
        else:
            i += 1
    
    return errors

if __name__ == '__main__':
    script_dir = Path(__file__).resolve().parent
    locale_dir = script_dir / 'locale'
    
    for lang in ['en', 'uz']:
        po_file = locale_dir / lang / 'LC_MESSAGES' / 'django.po'
        if po_file.exists():
            print(f"\nПроверка {po_file}...")
            errors = check_po_file(po_file)
            if errors:
                print(f"Найдено {len(errors)} ошибок:")
                for error in errors[:10]:  # Показываем первые 10 ошибок
                    print(f"  - {error}")
            else:
                print("  ✓ Файл выглядит корректно")

