import os
import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class ServicesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services"

    def ready(self):
        """Выполняется при запуске приложения."""
        # Проверяем, что мы не в миграции или других командах управления
        import sys
        if any(cmd in sys.argv for cmd in ["migrate", "makemigrations", "collectstatic", "shell", "test"]):
            return

        # Проверяем, что база данных готова
        try:
            from django.db import connection
            connection.ensure_connection()
        except Exception:
            return

        # Импортируем здесь, чтобы избежать циклических импортов
        try:
            from django.contrib.auth import get_user_model

            User = get_user_model()

            # Создаём суперпользователя из переменных окружения
            phone = os.environ.get("DJANGO_SUPERUSER_PHONE")
            password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
            name = os.environ.get("DJANGO_SUPERUSER_NAME", "Admin")

            if not phone or not password:
                return

            if not User.objects.filter(phone=phone).exists():
                User.objects.create_superuser(phone=phone, name=name, password=password)
                logger.info(f"✅ Суперпользователь создан: {name} ({phone})")
        except Exception as e:
            # Игнорируем ошибки при первом запуске (например, таблицы ещё не созданы)
            logger.debug(f"Не удалось создать суперпользователя (это нормально при первом запуске): {e}")
    verbose_name = "Сервис AliHouse"

