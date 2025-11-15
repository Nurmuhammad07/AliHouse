from django.urls import path

from .api_views import (
    CRMCustomerListAPIView,
    CRMCustomerUpdateAPIView,
    CRMOrderCommentCreateAPIView,
    CRMOrderListAPIView,
    CRMOrderUpdateAPIView,
    FeedbackCreateAPIView,
    OrderCreateAPIView,
    OrderRetrieveAPIView,
    ServiceListAPIView,
)

urlpatterns = [
    path("services/", ServiceListAPIView.as_view(), name="api-services"),
    path("orders/", OrderCreateAPIView.as_view(), name="api-orders-create"),
    path("orders/<int:pk>/", OrderRetrieveAPIView.as_view(), name="api-orders-detail"),
    path("feedback/", FeedbackCreateAPIView.as_view(), name="api-feedback-create"),
    path("crm/orders/", CRMOrderListAPIView.as_view(), name="api-crm-orders"),
    path("crm/orders/<int:pk>/", CRMOrderUpdateAPIView.as_view(), name="api-crm-order-update"),
    path("crm/orders/<int:pk>/comments/", CRMOrderCommentCreateAPIView.as_view(), name="api-crm-order-comment"),
    path("crm/customers/", CRMCustomerListAPIView.as_view(), name="api-crm-customers"),
    path("crm/customers/<int:pk>/", CRMCustomerUpdateAPIView.as_view(), name="api-crm-customer-update"),
]

