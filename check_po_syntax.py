#!/usr/bin/env python
"""Проверка синтаксиса файлов .po."""
import re
from pathlib import Path

def check_po_file(file_path):
    """Проверяет синтаксис файла .po и возвращает список ошибок."""
    errors = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    in_msgid = False
    in_msgstr = False
    msgid_lines = []
    msgstr_lines = []
    line_num = 0
    
    while i < len(lines):
        line_num = i + 1
        line = lines[i]
        stripped = line.strip()
        
        # Пропускаем комментарии
        if stripped.startswith('#'):
            i += 1
            continue
        
        # Пропускаем пустые строки
        if not stripped:
            if in_msgid or in_msgstr:
                # Пустая строка внутри msgid/msgstr - это нормально для многострочных
                pass
            i += 1
            continue
        
        # Проверяем msgid
        if stripped.startswith('msgid '):
            if in_msgid:
                errors.append(f"Строка {line_num}: новый msgid начался до завершения предыдущего")
            in_msgid = True
            in_msgstr = False
            msgid_lines = [stripped]
            i += 1
            
            # Проверяем многострочный msgid
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line:
                    break
                if next_line.startswith('"') and not next_line.startswith('msg'):
                    msgid_lines.append(next_line)
                    i += 1
                elif next_line.startswith('msgstr '):
                    break
                else:
                    break
            
            # Проверяем, что msgid правильно закрыт
            msgid_text = ' '.join(msgid_lines)
            if not (msgid_text.endswith('"') or 'msgid ""' in msgid_text):
                errors.append(f"Строка {line_num}: msgid не закрыт правильно: {msgid_text[:50]}")
        
        # Проверяем msgstr
        elif stripped.startswith('msgstr '):
            if not in_msgid:
                errors.append(f"Строка {line_num}: msgstr без msgid")
            in_msgstr = True
            in_msgid = False
            msgstr_lines = [stripped]
            i += 1
            
            # Проверяем многострочный msgstr
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line:
                    break
                if next_line.startswith('"') and not next_line.startswith('msg'):
                    msgstr_lines.append(next_line)
                    i += 1
                elif next_line.startswith('msgid '):
                    break
                else:
                    break
            
            # Проверяем, что msgstr правильно закрыт
            msgstr_text = ' '.join(msgstr_lines)
            if not (msgstr_text.endswith('"') or 'msgstr ""' in msgstr_text):
                errors.append(f"Строка {line_num}: msgstr не закрыт правильно: {msgstr_text[:50]}")
        else:
            # Неожиданная строка
            if not (stripped.startswith('"') or stripped.startswith('msg')):
                errors.append(f"Строка {line_num}: неожиданная строка: {stripped[:50]}")
            i += 1
    
    return errors

if __name__ == '__main__':
    script_dir = Path(__file__).resolve().parent
    locale_dir = script_dir / 'locale'
    
    all_errors = []
    for lang in ['en', 'uz']:
        po_file = locale_dir / lang / 'LC_MESSAGES' / 'django.po'
        if po_file.exists():
            print(f"\nПроверка {po_file.name}...")
            errors = check_po_file(po_file)
            if errors:
                print(f"✗ Найдено {len(errors)} ошибок:")
                for error in errors[:20]:
                    print(f"  - {error}")
                all_errors.extend([(lang, e) for e in errors])
            else:
                print(f"✓ Файл {lang} синтаксически корректен")
    
    if all_errors:
        print(f"\n✗ Всего найдено {len(all_errors)} ошибок")
        sys.exit(1)
    else:
        print("\n✓ Все файлы синтаксически корректны")

