from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import ContactRequest, Customer, Feedback, Order, OrderComment, Service, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("phone",)
    list_display = ("phone", "name", "role", "is_staff", "is_active")
    search_fields = ("phone", "name")
    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        (_("Персональные данные"), {"fields": ("name", "email")}),
        (_("Права доступа"), {"fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Системная информация"), {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone", "name", "password1", "password2", "role", "is_staff", "is_active"),
            },
        ),
    )
    list_filter = ("role", "is_staff", "is_active")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("get_title_display", "price", "price_type", "is_active", "created_at")
    list_filter = ("is_active", "price_type")
    search_fields = ("title_ru", "title_en", "title_uz", "title", "description_ru", "description_en", "description_uz", "description")
    
    def get_title_display(self, obj):
        """Отображает название на русском для списка."""
        return obj.get_title('ru') or obj.title or "-"
    get_title_display.short_description = _("Название")
    
    fieldsets = (
        (_("Изображение"), {
            "fields": ("image",)
        }),
        (_("Русский язык"), {
            "fields": ("title_ru", "description_ru", "detailed_description_ru", "history_achievements_ru")
        }),
        (_("Английский язык"), {
            "fields": ("title_en", "description_en", "detailed_description_en", "history_achievements_en")
        }),
        (_("Узбекский язык"), {
            "fields": ("title_uz", "description_uz", "detailed_description_uz", "history_achievements_uz")
        }),
        (_("Старые поля (fallback)"), {
            "fields": ("title", "description", "detailed_description", "history_achievements"),
            "classes": ("collapse",),
            "description": _("Используются только если не заполнены языковые версии")
        }),
        (_("Ценообразование"), {
            "fields": ("price_type", "price", "price_unit", "min_price"),
            "description": _("Настройка типа расчета цены и базовых параметров")
        }),
        (_("Настройки"), {
            "fields": ("is_active", "created_at")
        }),
    )
    readonly_fields = ("created_at",)


class FeedbackInline(admin.StackedInline):
    model = Feedback
    extra = 0
    readonly_fields = ("created_at",)


class OrderCommentInline(admin.TabularInline):
    model = OrderComment
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "service", "status", "priority", "assigned_to", "calculated_price", "created_at")
    list_filter = ("status", "priority", "service")
    search_fields = ("id", "user__phone", "customer__phone")
    inlines = [FeedbackInline, OrderCommentInline]
    autocomplete_fields = ("user", "service", "assigned_to", "customer")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (_("Основная информация"), {
            "fields": ("user", "customer", "service", "status", "priority", "assigned_to")
        }),
        (_("Детали заказа"), {
            "fields": ("details", "internal_notes")
        }),
        (_("Параметры расчета цены"), {
            "fields": ("price_calculation_sqm", "price_calculation_hours", "price_calculation_items", "calculated_price"),
            "description": _("Параметры, указанные пользователем при создании заказа")
        }),
        (_("Системная информация"), {
            "fields": ("created_at", "updated_at")
        }),
    )


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("order", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("order__id", "order__user__phone")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "last_order_at", "created_at")
    search_fields = ("name", "phone")
    readonly_fields = ("created_at", "last_order_at")


@admin.register(OrderComment)
class OrderCommentAdmin(admin.ModelAdmin):
    list_display = ("order", "operator", "created_at")
    search_fields = ("order__id", "operator__phone")
    autocomplete_fields = ("order", "operator")


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "phone", "email", "status", "assigned_to", "created_at")
    list_filter = ("status", "assigned_to", "created_at")
    search_fields = ("phone", "email", "telegram", "instagram", "message")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (_("Контактная информация"), {"fields": ("phone", "email", "telegram", "instagram")}),
        (_("Сообщение"), {"fields": ("message",)}),
        (_("Управление"), {"fields": ("status", "assigned_to", "internal_notes")}),
        (_("Системная информация"), {"fields": ("created_at", "updated_at")}),
    )

