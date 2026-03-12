from django.urls import path
from .views import ReviewRate, ReviewByBook

urlpatterns = [
    path("reviews/rate/", ReviewRate.as_view()),
    path("reviews/book/<int:book_id>/", ReviewByBook.as_view()),
]
