import os
import requests
from django.db.models import Avg
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.openapi import AutoSchema

from .models import Review

BOOK_SERVICE_URL = os.environ.get("BOOK_SERVICE_URL", "http://book-service:8000")


def _book_exists(book_id):
    try:
        r = requests.get(f"{BOOK_SERVICE_URL}/api/books/{book_id}/", timeout=3)
        return r.status_code == 200
    except requests.RequestException:
        return False


class ReviewRate(APIView):
    schema = AutoSchema()

    """POST /api/reviews/rate/ {"book_id": 1, "customer_id": 1, "rating": 5, "comment": "..."} – FR5."""

    def post(self, request):
        book_id = request.data.get("book_id")
        customer_id = request.data.get("customer_id")
        rating = request.data.get("rating")
        comment = request.data.get("comment", "")
        if book_id is None or customer_id is None or rating is None:
            return Response({"error": "book_id, customer_id, rating required"}, status=status.HTTP_400_BAD_REQUEST)
        if not (1 <= rating <= 5):
            return Response({"error": "rating must be 1-5"}, status=status.HTTP_400_BAD_REQUEST)
        if not _book_exists(book_id):
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        obj, created = Review.objects.update_or_create(
            book_id=book_id,
            customer_id=customer_id,
            defaults={"rating": rating, "comment": comment},
        )
        return Response({
            "id": obj.id,
            "book_id": obj.book_id,
            "customer_id": obj.customer_id,
            "rating": obj.rating,
            "comment": obj.comment,
            "created": created,
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class ReviewByBook(APIView):
    schema = AutoSchema()

    """GET /api/reviews/book/<book_id>/ – danh sách đánh giá + điểm trung bình."""

    def get(self, request, book_id):
        reviews = Review.objects.filter(book_id=book_id).order_by("-created_at")
        avg = reviews.aggregate(avg_rating=Avg("rating"))["avg_rating"]
        data = [{"id": r.id, "customer_id": r.customer_id, "rating": r.rating, "comment": r.comment, "created_at": r.created_at.isoformat()} for r in reviews]
        return Response({"book_id": book_id, "average_rating": float(avg) if avg is not None else None, "reviews": data})
