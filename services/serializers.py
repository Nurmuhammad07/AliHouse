from rest_framework import serializers

from .models import Customer, Feedback, Order, OrderComment, Service, User


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ("id", "title", "price", "description")


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = Order
        fields = ("id", "user", "service", "details", "status", "created_at")
        read_only_fields = ("id", "status", "created_at")

    def validate_service(self, service: Service):
        if not service.is_active:
            raise serializers.ValidationError("Услуга недоступна.")
        return service


class OrderDetailSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    user = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = Order
        fields = ("id", "user", "service", "details", "status", "created_at", "updated_at")


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ("order", "rating", "text", "created_at")
        read_only_fields = ("created_at",)

    def validate_order(self, order: Order):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            raise serializers.ValidationError("Требуется авторизация.")
        if order.user != request.user:
            raise serializers.ValidationError("Нельзя оставить отзыв для чужой заявки.")
        if order.status != Order.Status.DONE:
            raise serializers.ValidationError("Отзыв можно оставить только после завершения заявки.")
        if hasattr(order, "feedback"):
            raise serializers.ValidationError("Для этой заявки отзыв уже существует.")
        return order


class CRMOrderSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    service = ServiceSerializer(read_only=True)
    assigned_to = serializers.CharField(source="assigned_to.name", default=None)

    class Meta:
        model = Order
        fields = (
            "id",
            "customer",
            "service",
            "status",
            "priority",
            "assigned_to",
            "details",
            "internal_notes",
            "created_at",
            "updated_at",
        )

    def get_customer(self, obj: Order):
        if obj.customer:
            return {"name": obj.customer.name, "phone": obj.customer.phone}
        return {"name": obj.user.name, "phone": obj.user.phone}


class CRMOrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("status", "priority", "assigned_to", "internal_notes")

    def validate_assigned_to(self, value: User | None):
        if value and value.role not in {User.Role.ADMIN, User.Role.OPERATOR}:
            raise serializers.ValidationError("Назначить можно только оператора или администратора.")
        return value


class CRMOrderCommentSerializer(serializers.ModelSerializer):
    operator = serializers.CharField(source="operator.name", read_only=True)

    class Meta:
        model = OrderComment
        fields = ("id", "order", "operator", "text", "created_at")
        read_only_fields = ("id", "operator", "created_at", "order")


class CRMCustomerSerializer(serializers.ModelSerializer):
    orders_count = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ("id", "name", "phone", "notes", "last_order_at", "orders_count")

    def get_orders_count(self, obj: Customer):
        return obj.orders.count()

