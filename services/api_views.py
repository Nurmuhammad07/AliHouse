from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Customer, Feedback, Order, Service
from .permissions import IsOperatorOrAdmin
from .serializers import (
    CRMCustomerSerializer,
    CRMOrderCommentSerializer,
    CRMOrderSerializer,
    CRMOrderUpdateSerializer,
    FeedbackSerializer,
    OrderDetailSerializer,
    OrderSerializer,
    ServiceSerializer,
)


class ServiceListAPIView(generics.ListAPIView):
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]


class OrderCreateAPIView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        customer = Customer.objects.matching_user(self.request.user, serializer.validated_data.get("service"))
        serializer.save(user=self.request.user, customer=customer)


class OrderRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    queryset = Order.objects.all()

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related("service", "user")


class FeedbackCreateAPIView(generics.CreateAPIView):
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()

    def get_queryset(self):
        return Feedback.objects.filter(order__user=self.request.user)


class CRMOrderListAPIView(generics.ListAPIView):
    serializer_class = CRMOrderSerializer
    permission_classes = [IsOperatorOrAdmin]

    def get_queryset(self):
        qs = Order.objects.select_related("customer", "service", "assigned_to")
        status = self.request.query_params.get("status")
        priority = self.request.query_params.get("priority")
        operator = self.request.query_params.get("operator")
        phone = self.request.query_params.get("phone")
        if status:
            qs = qs.filter(status=status)
        if priority:
            qs = qs.filter(priority=priority)
        if operator:
            qs = qs.filter(assigned_to_id=operator)
        if phone:
            qs = qs.filter(customer__phone__icontains=phone)
        return qs


class CRMOrderUpdateAPIView(generics.UpdateAPIView):
    serializer_class = CRMOrderUpdateSerializer
    permission_classes = [IsOperatorOrAdmin]
    queryset = Order.objects.select_related("customer", "assigned_to")


class CRMOrderCommentCreateAPIView(generics.CreateAPIView):
    serializer_class = CRMOrderCommentSerializer
    permission_classes = [IsOperatorOrAdmin]

    def perform_create(self, serializer):
        order = get_object_or_404(Order, pk=self.kwargs["pk"])
        serializer.save(order=order, operator=self.request.user)


class CRMCustomerListAPIView(generics.ListAPIView):
    serializer_class = CRMCustomerSerializer
    permission_classes = [IsOperatorOrAdmin]

    def get_queryset(self):
        qs = Customer.objects.all()
        phone = self.request.query_params.get("phone")
        if phone:
            qs = qs.filter(phone__icontains=phone)
        return qs


class CRMCustomerUpdateAPIView(generics.UpdateAPIView):
    serializer_class = CRMCustomerSerializer
    permission_classes = [IsOperatorOrAdmin]
    queryset = Customer.objects.all()

