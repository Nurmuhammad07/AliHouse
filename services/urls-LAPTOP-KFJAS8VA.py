from django.contrib.auth.views import LoginView
from django.urls import path
from django.views.i18n import set_language

from .forms import PhoneAuthenticationForm
from .views import (
    ContactRequestCreateView,
    ContactRequestSuccessView,
    DashboardView,
    FeedbackCreateView,
    LandingPageView,
    OrderCreateView,
    OrderDetailView,
    ServiceDetailView,
    ServiceListView,
    SignUpView,
    logout_view,
)

app_name = "services"

urlpatterns = [
    path("i18n/setlang/", set_language, name="set_language"),
    path("", LandingPageView.as_view(), name="landing"),
    path("catalog/", ServiceListView.as_view(), name="service_list"),
    path("services/<int:pk>/", ServiceDetailView.as_view(), name="service_detail"),
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
    path("contact/", ContactRequestCreateView.as_view(), name="contact_request"),
    path("contact/success/", ContactRequestSuccessView.as_view(), name="contact_success"),
]

