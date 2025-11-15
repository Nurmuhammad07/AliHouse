from __future__ import annotations

from typing import Any

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def _clean_phone(self, phone: str) -> str:
        return "".join(ch for ch in phone if ch.isdigit() or ch == "+")

    def create_user(self, phone: str, name: str, password: str | None = None, **extra_fields: Any):
        if not phone:
            raise ValueError("Phone number is required")
        if not name:
            raise ValueError("Name is required")
        phone = self._clean_phone(phone)
        user = self.model(phone=phone, name=name.strip(), **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone: str, name: str, password: str, **extra_fields: Any):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.ADMIN)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(phone, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = "admin", "Администратор"
        OPERATOR = "operator", "Оператор"
        USER = "user", "Клиент"

    phone = models.CharField("Телефон", max_length=20, unique=True)
    name = models.CharField("Имя", max_length=255)
    email = models.EmailField("Email", blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    role = models.CharField("Роль", max_length=20, choices=Role.choices, default=Role.USER)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    def __str__(self) -> str:
        return f"{self.name} ({self.phone})"


class Service(models.Model):
    title = models.CharField("Название", max_length=255)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    description = models.TextField("Описание", blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self) -> str:
        return self.title


class CustomerQuerySet(models.QuerySet):
    def search(self, term: str | None):
        if term:
            return self.filter(phone__icontains=term)
        return self


class CustomerManager(models.Manager.from_queryset(CustomerQuerySet)):
    def matching_user(self, user: User | None, service: Service | None = None) -> "Customer":
        if user is None:
            raise ValueError("user is required to match customer")
        customer, _ = self.get_or_create(
            user=user,
            defaults={
                "name": user.name,
                "phone": user.phone,
                "last_order_at": timezone.now(),
            },
        )
        return customer


class Customer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer_profile",
    )
    name = models.CharField("Имя", max_length=255)
    phone = models.CharField("Телефон", max_length=20, unique=True)
    notes = models.TextField("Заметки", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_order_at = models.DateTimeField("Последний заказ", null=True, blank=True)

    objects = CustomerManager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self) -> str:
        return f"{self.name} ({self.phone})"


class Order(models.Model):
    class Status(models.TextChoices):
        CREATED = "created", "Новая"
        ACCEPTED = "accepted", "Принята"
        IN_PROGRESS = "in_progress", "В работе"
        DONE = "done", "Завершена"
        CANCELLED = "cancelled", "Отменена"

    class Priority(models.TextChoices):
        NORMAL = "normal", "Обычный"
        HIGH = "high", "Высокий"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Клиент",
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="CRM клиент",
    )
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="orders", verbose_name="Услуга")
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.CREATED)
    priority = models.CharField("Приоритет", max_length=20, choices=Priority.choices, default=Priority.NORMAL)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_orders",
        null=True,
        blank=True,
        verbose_name="Ответственный оператор",
    )
    details = models.TextField("Комментарий", blank=True)
    internal_notes = models.TextField("Внутренние заметки", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

    def __str__(self) -> str:
        return f"#{self.pk} {self.service} для {self.user.phone}"

    def save(self, *args, **kwargs):
        if not self.customer and self.user_id:
            self.customer = Customer.objects.matching_user(self.user, self.service)
        is_new = self._state.adding
        previous_status = None
        if not is_new:
            previous_status = self.__class__.objects.get(pk=self.pk).status
        super().save(*args, **kwargs)
        if self.customer:
            should_update = False
            timestamp = self.updated_at if self.updated_at else timezone.now()
            if is_new and not self.customer.last_order_at:
                self.customer.last_order_at = self.created_at
                should_update = True
            elif self.status in {self.Status.ACCEPTED, self.Status.IN_PROGRESS, self.Status.DONE}:
                if previous_status != self.status or not self.customer.last_order_at:
                    if not self.customer.last_order_at or self.customer.last_order_at < timestamp:
                        self.customer.last_order_at = timestamp
                        should_update = True
            if should_update:
                self.customer.save(update_fields=["last_order_at"])


class OrderComment(models.Model):
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="comments", verbose_name="Заявка")
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="order_comments",
        verbose_name="Оператор",
    )
    text = models.TextField("Комментарий")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Комментарий к заявке"
        verbose_name_plural = "Комментарии к заявкам"

    def __str__(self) -> str:
        return f"Комментарий {self.operator} для заказа #{self.order_id}"


class Feedback(models.Model):
    order = models.OneToOneField("Order", on_delete=models.CASCADE, related_name="feedback", verbose_name="Заявка")
    rating = models.PositiveSmallIntegerField("Оценка", choices=[(i, str(i)) for i in range(1, 6)], default=5)
    text = models.TextField("Комментарий", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self) -> str:
        return f"Отзыв #{self.order_id}"

