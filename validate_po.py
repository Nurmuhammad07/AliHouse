#!/usr/bin/env python
"""Валидация файлов .po."""
import os
import sys
from pathlib import Path

# Установка рабочей директории
script_dir = Path(__file__).resolve().parent
os.chdir(str(script_dir))

# Проверка файлов .po вручную
def validate_po_syntax(file_path):
    """Проверяет синтаксис файла .po."""
    errors = []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    i = 0
    msgid_count = 0
    msgstr_count = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Пропускаем комментарии
        if line.startswith('#'):
            i += 1
            continue
        
        # Пропускаем пустые строки
        if not line:
            i += 1
            continue
        
        # Проверяем msgid
        if line.startswith('msgid '):
            msgid_count += 1
            # Проверяем, что строка правильно закрыта
            if not (line.endswith('"') or line == 'msgid ""'):
                # Многострочный msgid
                i += 1
                while i < len(lines) and lines[i].strip().startswith('"'):
                    if lines[i].strip().endswith('"'):
                        break
                    i += 1
                else:
                    errors.append(f"Строка {i+1}: незакрытый msgid")
            
            # Ищем соответствующий msgstr
            i += 1
            # Пропускаем пустые строки
            while i < len(lines) and not lines[i].strip():
                i += 1
            
            if i >= len(lines):
                errors.append(f"Строка {i}: msgid без msgstr в конце файла")
                break
            
            if not lines[i].strip().startswith('msgstr '):
                errors.append(f"Строка {i+1}: ожидается msgstr после msgid, найдено: {lines[i][:50]}")
                i += 1
                continue
            
            msgstr_count += 1
            i += 1
        elif line.startswith('msgstr '):
            # msgstr без msgid
            if msgstr_count >= msgid_count:
                errors.append(f"Строка {i+1}: msgstr без соответствующего msgid")
            msgstr_count += 1
            i += 1
        else:
            i += 1
    
    if msgid_count != msgstr_count:
        errors.append(f"Несоответствие: {msgid_count} msgid, {msgstr_count} msgstr")
    
    return errors

if __name__ == '__main__':
    locale_dir = script_dir / 'locale'
    
    for lang in ['en', 'uz']:
        po_file = locale_dir / lang / 'LC_MESSAGES' / 'django.po'
        if po_file.exists():
            print(f"\nПроверка {po_file.name}...")
            errors = validate_po_syntax(po_file)
            if errors:
                print(f"Найдено {len(errors)} ошибок:")
                for error in errors[:20]:
                    print(f"  - {error}")
            else:
                print("  ✓ Синтаксис корректен")

