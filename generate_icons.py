#!/usr/bin/env python
"""
Скрипт для генерации иконок PWA из базового изображения.
Требует установки Pillow: pip install Pillow
"""
from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

# Размеры иконок
ICON_SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

# Цвета
BACKGROUND_COLOR = "#ff6b35"  # Оранжевый (accent color)
TEXT_COLOR = "#ffffff"  # Белый

def create_icon(size):
    """Создает иконку указанного размера."""
    # Создаем изображение
    img = Image.new('RGB', (size, size), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Пытаемся использовать шрифт, если доступен
    try:
        # Пробуем разные шрифты
        font_size = int(size * 0.4)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Рисуем текст "AH" (AliHouse)
    text = "AH"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Центрируем текст
    x = (size - text_width) / 2
    y = (size - text_height) / 2 - bbox[1]
    
    draw.text((x, y), text, fill=TEXT_COLOR, font=font)
    
    return img

def main():
    """Генерирует все иконки."""
    # Создаем директорию для иконок
    icons_dir = Path(__file__).parent / "static" / "icons"
    icons_dir.mkdir(parents=True, exist_ok=True)
    
    print("Генерация иконок PWA...")
    print(f"Директория: {icons_dir}")
    
    for size in ICON_SIZES:
        icon = create_icon(size)
        icon_path = icons_dir / f"icon-{size}x{size}.png"
        icon.save(icon_path, "PNG")
        print(f"✓ Создана иконка: {icon_path.name}")
    
    print(f"\n✓ Все иконки созданы в {icons_dir}")
    print("\nПримечание: Это простые иконки с текстом 'AH'.")
    print("Для production рекомендуется создать профессиональные иконки с логотипом.")

if __name__ == "__main__":
    try:
        main()
    except ImportError:
        print("Ошибка: Pillow не установлен.")
        print("Установите: pip install Pillow")
    except Exception as e:
        print(f"Ошибка: {e}")

