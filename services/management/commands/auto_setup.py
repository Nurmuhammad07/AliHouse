"""
Management command для автоматической настройки после деплоя.
Создаёт суперпользователя из переменных окружения, если его ещё нет.
"""
import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Автоматически создаёт суперпользователя из переменных окружения"

    def handle(self, *args, **options):
        phone = os.environ.get("DJANGO_SUPERUSER_PHONE")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        name = os.environ.get("DJANGO_SUPERUSER_NAME", "Admin")

        if not phone or not password:
            self.stdout.write(
                self.style.WARNING(
                    "DJANGO_SUPERUSER_PHONE и DJANGO_SUPERUSER_PASSWORD не установлены. "
                    "Пропускаю создание суперпользователя."
                )
            )
            return

        if User.objects.filter(phone=phone).exists():
            self.stdout.write(
                self.style.SUCCESS(f"Суперпользователь с телефоном {phone} уже существует.")
            )
            return

        try:
            User.objects.create_superuser(phone=phone, name=name, password=password)
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Суперпользователь создан: {name} ({phone})"
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Ошибка при создании суперпользователя: {e}")
            )

