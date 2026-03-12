from django.urls import path
from .views import OrderCreate, OrderList

urlpatterns = [
    path("orders/create/", OrderCreate.as_view()),
    path("orders/", OrderList.as_view()),
]
