from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from drf_spectacular.openapi import AutoSchema

SpectacularAPIView.schema = AutoSchema()

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("customers.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("static/<path:path>", serve, {"document_root": settings.BASE_DIR / "static"}),
]
