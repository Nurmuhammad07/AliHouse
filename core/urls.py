from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(("services.urls", "services"), namespace="services")),
    path("crm/", include(("services.crm_urls", "crm"), namespace="crm")),
    path("api/auth/token/", obtain_auth_token, name="api-token"),
    path("api/", include("services.api_urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

