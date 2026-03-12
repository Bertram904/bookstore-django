from django.urls import path
from .views import BookListCreate, BookDetail, BookBatch

urlpatterns = [
    path("books/", BookListCreate.as_view()),
    path("books/batch/", BookBatch.as_view()),
    path("books/<int:pk>/", BookDetail.as_view()),
]
