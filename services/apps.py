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

        # Откладываем создание суперпользователя до полной инициализации Django
        # Используем threading для выполнения после полной загрузки
        import threading

        def create_superuser_delayed():
            """Создаёт суперпользователя после полной загрузки Django."""
            try:
                from django.apps import apps
                # Ждём, пока все приложения загрузятся
                if not apps.ready:
                    return

                from django.contrib.auth import get_user_model
                from django.db import connection

                # Проверяем, что база данных готова
                connection.ensure_connection()

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
                # Игнорируем ошибки при первом запуске
                logger.debug(f"Не удалось создать суперпользователя: {e}")

        # Запускаем в отдельном потоке с небольшой задержкой
        thread = threading.Thread(target=create_superuser_delayed, daemon=True)
        thread.start()
    verbose_name = "Сервис AliHouse"

