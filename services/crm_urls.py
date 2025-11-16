from django.urls import path

from .views import (
    CRMCustomerDetailView,
    CRMCustomerListView,
    CRMDashboardView,
    CRMContactRequestDetailView,
    CRMContactRequestListView,
    CRMOrderDetailView,
    CRMOrderListView,
    CRMStatisticsView,
    CRMUsersListView,
)

app_name = "crm"

urlpatterns = [
    path("", CRMDashboardView.as_view(), name="dashboard"),
    path("orders/", CRMOrderListView.as_view(), name="orders"),
    path("orders/<int:pk>/", CRMOrderDetailView.as_view(), name="order-detail"),
    path("customers/", CRMCustomerListView.as_view(), name="customers"),
    path("customers/<int:pk>/", CRMCustomerDetailView.as_view(), name="customer-detail"),
    path("users/", CRMUsersListView.as_view(), name="users"),
    path("contact-requests/", CRMContactRequestListView.as_view(), name="contact-requests"),
    path("contact-requests/<int:pk>/", CRMContactRequestDetailView.as_view(), name="contact-request-detail"),
    path("statistics/", CRMStatisticsView.as_view(), name="statistics"),
]

