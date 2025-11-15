"""
Management command для создания суперпользователя.
Использование: python manage.py create_admin
"""
import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Создаёт суперпользователя для доступа к админ-панели"

    def add_arguments(self, parser):
        parser.add_argument(
            '--phone',
            type=str,
            help='Номер телефона суперпользователя',
            default=os.environ.get("DJANGO_SUPERUSER_PHONE", "+998")
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Пароль суперпользователя',
            default=os.environ.get("DJANGO_SUPERUSER_PASSWORD", "nurik123")
        )
        parser.add_argument(
            '--name',
            type=str,
            help='Имя суперпользователя',
            default=os.environ.get("DJANGO_SUPERUSER_NAME", "Admin")
        )

    def handle(self, *args, **options):
        phone = options['phone']
        password = options['password']
        name = options['name']

        if not phone or not password:
            self.stdout.write(
                self.style.ERROR(
                    "❌ Укажите телефон и пароль для суперпользователя.\n"
                    "Использование: python manage.py create_admin --phone +998 --password ваш_пароль"
                )
            )
            return

        # Проверяем, существует ли уже пользователь
        if User.objects.filter(phone=phone).exists():
            user = User.objects.get(phone=phone)
            if user.is_superuser and user.is_staff:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Суперпользователь уже существует: {name} ({phone})")
                )
                self.stdout.write("\nДанные для входа в админ-панель:")
                self.stdout.write(f"  Телефон: {phone}")
                self.stdout.write(f"  Пароль: {password}")
            else:
                # Делаем существующего пользователя суперпользователем
                user.is_superuser = True
                user.is_staff = True
                user.role = User.Role.ADMIN
                user.set_password(password)
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Пользователь {name} ({phone}) теперь суперпользователь")
                )
                self.stdout.write("\nДанные для входа в админ-панель:")
                self.stdout.write(f"  Телефон: {phone}")
                self.stdout.write(f"  Пароль: {password}")
        else:
            # Создаем нового суперпользователя
            try:
                User.objects.create_superuser(phone=phone, name=name, password=password)
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Суперпользователь создан: {name} ({phone})")
                )
                self.stdout.write("\nДанные для входа в админ-панель:")
                self.stdout.write(f"  Телефон: {phone}")
                self.stdout.write(f"  Пароль: {password}")
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Ошибка при создании суперпользователя: {e}")
                )

