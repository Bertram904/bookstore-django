import os
import requests
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.openapi import AutoSchema

BOOK_SERVICE_URL = os.environ.get("BOOK_SERVICE_URL", "http://book-service:8000")


class CatalogBookList(APIView):
    schema = AutoSchema()

    """GET /api/catalog/books/ – proxy danh sách sách từ book-service."""

    def get(self, request):
        try:
            r = requests.get(f"{BOOK_SERVICE_URL}/api/books/", timeout=5)
            r.raise_for_status()
            return Response(r.json())
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)
