from django.urls import path
from .views import Dashboard

urlpatterns = [
    path("manager/dashboard/", Dashboard.as_view()),
]
