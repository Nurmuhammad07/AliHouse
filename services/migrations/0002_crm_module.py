from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


def bootstrap_customers(apps, schema_editor):
    User = apps.get_model("services", "User")
    Customer = apps.get_model("services", "Customer")
    Order = apps.get_model("services", "Order")

    customer_cache = {}
    for user in User.objects.all():
        customer, _ = Customer.objects.get_or_create(
            user_id=user.id,
            defaults={"name": user.name, "phone": user.phone, "created_at": user.date_joined},
        )
        customer_cache[user.id] = customer

    for order in Order.objects.all():
        customer = customer_cache.get(order.user_id)
        if customer and order.customer_id is None:
            order.customer = customer
            if order.status == "new":
                order.status = "created"
            order.save(update_fields=["customer", "status"])
            if not customer.last_order_at or customer.last_order_at < order.created_at:
                customer.last_order_at = order.created_at
                customer.save(update_fields=["last_order_at"])


class Migration(migrations.Migration):
    dependencies = [
        ("services", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[("admin", "Администратор"), ("operator", "Оператор"), ("user", "Клиент")],
                default="user",
                max_length=20,
                verbose_name="Роль",
            ),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name="Customer",
            fields=[
                (
                    "id",
                    models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                ("name", models.CharField(max_length=255, verbose_name="Имя")),
                ("phone", models.CharField(max_length=20, unique=True, verbose_name="Телефон")),
                ("notes", models.TextField(blank=True, verbose_name="Заметки")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("last_order_at", models.DateTimeField(blank=True, null=True, verbose_name="Последний заказ")),
                (
                    "user",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="customer_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="OrderComment",
            fields=[
                (
                    "id",
                    models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                ("text", models.TextField(verbose_name="Комментарий")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "operator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="order_comments",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Оператор",
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="services.order",
                        verbose_name="Заявка",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="order",
            name="assigned_to",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="assigned_orders",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Ответственный оператор",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="customer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="orders",
                to="services.customer",
                verbose_name="CRM клиент",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="internal_notes",
            field=models.TextField(blank=True, verbose_name="Внутренние заметки"),
        ),
        migrations.AddField(
            model_name="order",
            name="priority",
            field=models.CharField(
                choices=[("normal", "Обычный"), ("high", "Высокий")],
                default="normal",
                max_length=20,
                verbose_name="Приоритет",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("created", "Новая"),
                    ("accepted", "Принята"),
                    ("in_progress", "В работе"),
                    ("done", "Завершена"),
                    ("cancelled", "Отменена"),
                ],
                default="created",
                max_length=20,
                verbose_name="Статус",
            ),
        ),
        migrations.RunPython(bootstrap_customers, migrations.RunPython.noop),
    ]

