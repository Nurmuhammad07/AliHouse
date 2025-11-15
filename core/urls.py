from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(("services.urls", "services"), namespace="services")),
    path("crm/", include(("services.crm_urls", "crm"), namespace="crm")),
    path("api/auth/token/", obtain_auth_token, name="api-token"),
    path("api/", include("services.api_urls")),
    # PWA: Service Worker должен быть доступен из корня
    path("service-worker.js", RedirectView.as_view(url="/static/service-worker.js", permanent=False), name="service-worker"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

