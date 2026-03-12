import os
import requests
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.openapi import AutoSchema

BOOK_SERVICE_URL = os.environ.get("BOOK_SERVICE_URL", "http://book-service:8000")
COMMENT_RATE_SERVICE_URL = os.environ.get("COMMENT_RATE_SERVICE_URL", "http://comment-rate-service:8000")


class Recommend(APIView):
    schema = AutoSchema()

    """GET /api/recommend/?book_id=1 – gợi ý sách (đơn giản: lấy top-rated từ comment-rate, trộn với danh sách book)."""

    def get(self, request):
        limit = min(int(request.query_params.get("limit", 5)), 20)
        try:
            r_books = requests.get(f"{BOOK_SERVICE_URL}/api/books/", timeout=5)
            r_books.raise_for_status()
            books = r_books.json()
        except requests.RequestException:
            return Response({"recommendations": []})
        if not books:
            return Response({"recommendations": []})
        # Đơn giản: trả về N sách đầu (có thể mở rộng gọi comment-rate lấy top rated)
        recommendations = books[:limit]
        return Response({"recommendations": recommendations})
