from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Customer, Feedback, Order, OrderComment, Service, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("phone",)
    list_display = ("phone", "name", "role", "is_staff", "is_active")
    search_fields = ("phone", "name")
    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("Персональные данные", {"fields": ("name", "email")}),
        ("Права доступа", {"fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Системная информация", {"fields": ("last_login",)}),
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
    list_display = ("title", "price", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title",)


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
    list_display = ("id", "customer", "service", "status", "priority", "assigned_to", "created_at")
    list_filter = ("status", "priority", "service")
    search_fields = ("id", "user__phone", "customer__phone")
    inlines = [FeedbackInline, OrderCommentInline]
    autocomplete_fields = ("user", "service", "assigned_to", "customer")


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

