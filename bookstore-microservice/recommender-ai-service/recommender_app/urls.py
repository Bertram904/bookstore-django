from django.urls import path
from .views import Recommend

urlpatterns = [
    path("recommend/", Recommend.as_view()),
]
