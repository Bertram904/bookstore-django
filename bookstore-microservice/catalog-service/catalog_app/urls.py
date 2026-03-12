from django.urls import path
from .views import CatalogBookList

urlpatterns = [
    path("catalog/books/", CatalogBookList.as_view()),
]
