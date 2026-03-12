from django.conf import settings
from django.urls import path, include
from django.views.static import serve

urlpatterns = [path("", include("gateway.urls"))]

urlpatterns += [
    path("static/<path:path>", serve, {"document_root": settings.BASE_DIR / "gateway" / "static"}),
]
