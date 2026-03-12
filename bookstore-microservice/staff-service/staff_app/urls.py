from django.urls import path
from .views import StaffBookListCreate, StaffBookDetail

urlpatterns = [
    path("staff/books/", StaffBookListCreate.as_view()),
    path("staff/books/<int:pk>/", StaffBookDetail.as_view()),
]
