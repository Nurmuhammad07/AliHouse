from __future__ import annotations

from typing import Any

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


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
        ADMIN = "admin", _("Администратор")
        OPERATOR = "operator", _("Оператор")
        USER = "user", _("Клиент")

    phone = models.CharField(_("Телефон"), max_length=20, unique=True)
    name = models.CharField(_("Имя"), max_length=255)
    email = models.EmailField("Email", blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    role = models.CharField(_("Роль"), max_length=20, choices=Role.choices, default=Role.USER)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    def __str__(self) -> str:
        return f"{self.name} ({self.phone})"


class Service(models.Model):
    class PriceType(models.TextChoices):
        FIXED = "fixed", _("Фиксированная цена")
        PER_SQM = "per_sqm", _("За м²")
        PER_HOUR = "per_hour", _("За час")
        PER_ITEM = "per_item", _("За единицу")
        CUSTOM = "custom", _("Индивидуальный расчет")

    # Старые поля для обратной совместимости (используются как fallback)
    title = models.CharField(_("Название (старое)"), max_length=255, blank=True, help_text=_("Используется как fallback, если не заполнены языковые версии"))
    description = models.TextField(_("Краткое описание (старое)"), blank=True, help_text=_("Используется как fallback"))
    detailed_description = models.TextField(_("Детальное описание (старое)"), blank=True, help_text=_("Используется как fallback"))
    history_achievements = models.TextField(_("История и достижения (старое)"), blank=True, help_text=_("Используется как fallback"))
    
    # Поля для русского языка
    title_ru = models.CharField(_("Название (русский)"), max_length=255, blank=True)
    description_ru = models.TextField(_("Краткое описание (русский)"), blank=True)
    detailed_description_ru = models.TextField(_("Детальное описание (русский)"), blank=True, help_text=_("Полное описание услуги"))
    history_achievements_ru = models.TextField(_("История и достижения (русский)"), blank=True, help_text=_("История услуги, достижения, статистика"))
    
    # Поля для английского языка
    title_en = models.CharField(_("Название (английский)"), max_length=255, blank=True)
    description_en = models.TextField(_("Краткое описание (английский)"), blank=True)
    detailed_description_en = models.TextField(_("Детальное описание (английский)"), blank=True)
    history_achievements_en = models.TextField(_("История и достижения (английский)"), blank=True)
    
    # Поля для узбекского языка
    title_uz = models.CharField(_("Название (узбекский)"), max_length=255, blank=True)
    description_uz = models.TextField(_("Краткое описание (узбекский)"), blank=True)
    detailed_description_uz = models.TextField(_("Детальное описание (узбекский)"), blank=True)
    history_achievements_uz = models.TextField(_("История и достижения (узбекский)"), blank=True)
    
    price = models.DecimalField(_("Базовая цена"), max_digits=10, decimal_places=2, help_text=_("Базовая цена или цена за единицу"))
    price_type = models.CharField(_("Тип расчета цены"), max_length=20, choices=PriceType.choices, default=PriceType.FIXED)
    price_unit = models.CharField(_("Единица измерения"), max_length=50, blank=True, help_text=_("м², час, шт. и т.д."))
    min_price = models.DecimalField(_("Минимальная цена"), max_digits=10, decimal_places=2, null=True, blank=True, help_text=_("Минимальная стоимость услуги"))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title_ru", "title_en", "title_uz", "title"]
        verbose_name = _("Услуга")
        verbose_name_plural = _("Услуги")

    def get_title(self, language_code=None):
        """Возвращает название услуги на указанном языке или текущем языке пользователя."""
        if language_code is None:
            from django.utils import translation
            language_code = translation.get_language()
        
        title_field = f"title_{language_code}"
        if hasattr(self, title_field) and getattr(self, title_field):
            return getattr(self, title_field)
        # Fallback на старое поле или другие языки
        if self.title:
            return self.title
        # Пробуем другие языки
        for lang in ['ru', 'en', 'uz']:
            if lang != language_code:
                fallback_field = f"title_{lang}"
                if hasattr(self, fallback_field) and getattr(self, fallback_field):
                    return getattr(self, fallback_field)
        return _("Без названия")
    
    def get_description(self, language_code=None):
        """Возвращает описание услуги на указанном языке."""
        if language_code is None:
            from django.utils import translation
            language_code = translation.get_language()
        
        desc_field = f"description_{language_code}"
        if hasattr(self, desc_field) and getattr(self, desc_field):
            return getattr(self, desc_field)
        # Fallback
        if self.description:
            return self.description
        for lang in ['ru', 'en', 'uz']:
            if lang != language_code:
                fallback_field = f"description_{lang}"
                if hasattr(self, fallback_field) and getattr(self, fallback_field):
                    return getattr(self, fallback_field)
        return ""
    
    def get_detailed_description(self, language_code=None):
        """Возвращает детальное описание услуги на указанном языке."""
        if language_code is None:
            from django.utils import translation
            language_code = translation.get_language()
        
        desc_field = f"detailed_description_{language_code}"
        if hasattr(self, desc_field) and getattr(self, desc_field):
            return getattr(self, desc_field)
        # Fallback
        if self.detailed_description:
            return self.detailed_description
        for lang in ['ru', 'en', 'uz']:
            if lang != language_code:
                fallback_field = f"detailed_description_{lang}"
                if hasattr(self, fallback_field) and getattr(self, fallback_field):
                    return getattr(self, fallback_field)
        return ""
    
    def get_history_achievements(self, language_code=None):
        """Возвращает историю и достижения на указанном языке."""
        if language_code is None:
            from django.utils import translation
            language_code = translation.get_language()
        
        hist_field = f"history_achievements_{language_code}"
        if hasattr(self, hist_field) and getattr(self, hist_field):
            return getattr(self, hist_field)
        # Fallback
        if self.history_achievements:
            return self.history_achievements
        for lang in ['ru', 'en', 'uz']:
            if lang != language_code:
                fallback_field = f"history_achievements_{lang}"
                if hasattr(self, fallback_field) and getattr(self, fallback_field):
                    return getattr(self, fallback_field)
        return ""

    def __str__(self) -> str:
        # Используем русский язык по умолчанию для админки
        return self.get_title('ru') or self.title or _("Без названия")

    def calculate_price(self, **kwargs):
        """Рассчитывает цену на основе параметров."""
        if self.price_type == self.PriceType.FIXED:
            return self.price
        elif self.price_type == self.PriceType.PER_SQM:
            sqm = kwargs.get("sqm", 0)
            calculated = self.price * sqm
            if self.min_price:
                return max(calculated, self.min_price)
            return calculated
        elif self.price_type == self.PriceType.PER_HOUR:
            hours = kwargs.get("hours", 0)
            calculated = self.price * hours
            if self.min_price:
                return max(calculated, self.min_price)
            return calculated
        elif self.price_type == self.PriceType.PER_ITEM:
            items = kwargs.get("items", 0)
            calculated = self.price * items
            if self.min_price:
                return max(calculated, self.min_price)
            return calculated
        return self.price


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
    name = models.CharField(_("Имя"), max_length=255)
    phone = models.CharField(_("Телефон"), max_length=20, unique=True)
    notes = models.TextField(_("Заметки"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_order_at = models.DateTimeField(_("Последний заказ"), null=True, blank=True)

    objects = CustomerManager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Клиент")
        verbose_name_plural = _("Клиенты")

    def __str__(self) -> str:
        return f"{self.name} ({self.phone})"


class Order(models.Model):
    class Status(models.TextChoices):
        CREATED = "created", _("Новая")
        ACCEPTED = "accepted", _("Принята")
        IN_PROGRESS = "in_progress", _("В работе")
        DONE = "done", _("Завершена")
        CANCELLED = "cancelled", _("Отменена")

    class Priority(models.TextChoices):
        NORMAL = "normal", _("Обычный")
        HIGH = "high", _("Высокий")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name=_("Клиент"),
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name=_("CRM клиент"),
    )
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="orders", verbose_name=_("Услуга"))
    status = models.CharField(_("Статус"), max_length=20, choices=Status.choices, default=Status.CREATED)
    priority = models.CharField(_("Приоритет"), max_length=20, choices=Priority.choices, default=Priority.NORMAL)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_orders",
        null=True,
        blank=True,
        verbose_name=_("Ответственный оператор"),
    )
    details = models.TextField(_("Комментарий"), blank=True)
    internal_notes = models.TextField(_("Внутренние заметки"), blank=True)
    # Параметры расчета цены (для услуг с динамической ценой)
    price_calculation_sqm = models.DecimalField(_("Площадь (м²)"), max_digits=10, decimal_places=2, null=True, blank=True)
    price_calculation_hours = models.DecimalField(_("Количество часов"), max_digits=10, decimal_places=2, null=True, blank=True)
    price_calculation_items = models.IntegerField(_("Количество единиц"), null=True, blank=True)
    calculated_price = models.DecimalField(_("Рассчитанная цена"), max_digits=10, decimal_places=2, null=True, blank=True, help_text=_("Цена, рассчитанная на основе параметров"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Заявка")
        verbose_name_plural = _("Заявки")

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
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="comments", verbose_name=_("Заявка"))
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="order_comments",
        verbose_name=_("Оператор"),
    )
    text = models.TextField(_("Комментарий"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Комментарий к заявке")
        verbose_name_plural = _("Комментарии к заявкам")

    def __str__(self) -> str:
        return f"Комментарий {self.operator} для заказа #{self.order_id}"


class Feedback(models.Model):
    order = models.OneToOneField("Order", on_delete=models.CASCADE, related_name="feedback", verbose_name=_("Заявка"))
    rating = models.PositiveSmallIntegerField(_("Оценка"), choices=[(i, str(i)) for i in range(1, 6)], default=5)
    text = models.TextField(_("Комментарий"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Отзыв")
        verbose_name_plural = _("Отзывы")

    def __str__(self) -> str:
        return f"Отзыв #{self.order_id}"


class ContactRequest(models.Model):
    class Status(models.TextChoices):
        NEW = "new", _("Новая")
        IN_PROGRESS = "in_progress", _("В работе")
        CONTACTED = "contacted", _("Связались")
        CLOSED = "closed", _("Закрыта")

    phone = models.CharField(_("Телефон"), max_length=20)
    email = models.EmailField("Email", blank=True)
    telegram = models.CharField("Telegram", max_length=100, blank=True)
    instagram = models.CharField("Instagram", max_length=100, blank=True)
    message = models.TextField(_("Сообщение"))
    status = models.CharField(_("Статус"), max_length=20, choices=Status.choices, default=Status.NEW)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contact_requests",
        verbose_name=_("Ответственный оператор"),
    )
    internal_notes = models.TextField(_("Внутренние заметки"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Заявка обратной связи")
        verbose_name_plural = _("Заявки обратной связи")

    def __str__(self) -> str:
        return f"Заявка #{self.pk} от {self.phone}"

