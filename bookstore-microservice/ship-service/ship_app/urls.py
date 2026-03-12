from django.urls import path
from .views import ShipReserve, ShipRelease, ShipOptions

urlpatterns = [
    path("ship/reserve/", ShipReserve.as_view()),
    path("ship/<int:pk>/release/", ShipRelease.as_view()),
    path("ship/shippers/", ShipOptions.as_view()),
]
