from django.contrib.auth.views import LoginView
from django.urls import path

from .forms import PhoneAuthenticationForm
from .views import (
    DashboardView,
    FeedbackCreateView,
    LandingPageView,
    OrderCreateView,
    OrderDetailView,
    ServiceListView,
    SignUpView,
    logout_view,
)

app_name = "services"

urlpatterns = [
    path("", LandingPageView.as_view(), name="landing"),
    path("catalog/", ServiceListView.as_view(), name="service_list"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path(
        "login/",
        LoginView.as_view(
            template_name="registration/login.html",
            authentication_form=PhoneAuthenticationForm,
        ),
        name="login",
    ),
    path("logout/", logout_view, name="logout"),
    path("orders/new/", OrderCreateView.as_view(), name="order_create"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("feedback/<int:pk>/", FeedbackCreateView.as_view(), name="feedback"),
]

