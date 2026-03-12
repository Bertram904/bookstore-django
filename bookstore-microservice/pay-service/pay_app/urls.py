from django.urls import path
from .views import PayReserve, PayRelease

urlpatterns = [
    path("pay/reserve/", PayReserve.as_view()),
    path("pay/<int:pk>/release/", PayRelease.as_view()),
]
