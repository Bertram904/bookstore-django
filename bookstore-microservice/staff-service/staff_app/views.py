import os
import requests
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

BOOK_SERVICE_URL = os.environ.get("BOOK_SERVICE_URL", "http://book-service:8000")


class StaffBookListCreate(APIView):
    """FR2: Staff quản lý sách – proxy tới book-service."""

    def get(self, request):
        try:
            r = requests.get(f"{BOOK_SERVICE_URL}/api/books/", timeout=5)
            r.raise_for_status()
            return Response(r.json())
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

    def post(self, request):
        try:
            r = requests.post(f"{BOOK_SERVICE_URL}/api/books/", json=request.data, timeout=5)
            if r.status_code in (200, 201):
                return Response(r.json(), status=r.status_code)
            return Response(r.json() if r.text else {"error": "Book service error"}, status=r.status_code)
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)


class StaffBookDetail(APIView):
    def get(self, request, pk):
        try:
            r = requests.get(f"{BOOK_SERVICE_URL}/api/books/{pk}/", timeout=5)
            if r.status_code == 404:
                return Response(r.json(), status=404)
            r.raise_for_status()
            return Response(r.json())
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

    def put(self, request, pk):
        try:
            r = requests.put(f"{BOOK_SERVICE_URL}/api/books/{pk}/", json=request.data, timeout=5)
            return Response(r.json() if r.text else {}, status=r.status_code)
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

    def delete(self, request, pk):
        try:
            r = requests.delete(f"{BOOK_SERVICE_URL}/api/books/{pk}/", timeout=5)
            return Response(status=r.status_code)
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)
