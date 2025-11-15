from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .forms import PhoneAuthenticationForm
from .views import (
    DashboardView,
    FeedbackCreateView,
    OrderCreateView,
    OrderDetailView,
    ServiceListView,
    SignUpView,
)

app_name = "services"

urlpatterns = [
    path("", ServiceListView.as_view(), name="service_list"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path(
        "login/",
        LoginView.as_view(
            template_name="registration/login.html",
            authentication_form=PhoneAuthenticationForm,
        ),
        name="login",
    ),
    path("logout/", LogoutView.as_view(next_page="services:service_list"), name="logout"),
    path("orders/new/", OrderCreateView.as_view(), name="order_create"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("feedback/<int:pk>/", FeedbackCreateView.as_view(), name="feedback"),
]

