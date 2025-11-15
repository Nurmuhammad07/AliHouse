from django.urls import path

from .views import (
    CRMCustomerDetailView,
    CRMCustomerListView,
    CRMDashboardView,
    CRMOrderDetailView,
    CRMOrderListView,
)

app_name = "crm"

urlpatterns = [
    path("", CRMDashboardView.as_view(), name="dashboard"),
    path("orders/", CRMOrderListView.as_view(), name="orders"),
    path("orders/<int:pk>/", CRMOrderDetailView.as_view(), name="order-detail"),
    path("customers/", CRMCustomerListView.as_view(), name="customers"),
    path("customers/<int:pk>/", CRMCustomerDetailView.as_view(), name="customer-detail"),
]

