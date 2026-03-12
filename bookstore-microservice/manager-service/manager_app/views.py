import os
import requests
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.openapi import AutoSchema

CUSTOMER_SERVICE_URL = os.environ.get("CUSTOMER_SERVICE_URL", "http://customer-service:8000")
BOOK_SERVICE_URL = os.environ.get("BOOK_SERVICE_URL", "http://book-service:8000")
ORDER_SERVICE_URL = os.environ.get("ORDER_SERVICE_URL", "http://order-service:8000")


class Dashboard(APIView):
    schema = AutoSchema()

    """GET /api/manager/dashboard/ – tổng hợp số khách, số sách, số đơn (cho manager)."""

    def get(self, request):
        data = {"customers_count": 0, "books_count": 0, "orders_count": 0}
        try:
            r = requests.get(f"{CUSTOMER_SERVICE_URL}/api/customers/", timeout=3)
            if r.status_code == 200:
                data["customers_count"] = len(r.json())
        except requests.RequestException:
            pass
        try:
            r = requests.get(f"{BOOK_SERVICE_URL}/api/books/", timeout=3)
            if r.status_code == 200:
                data["books_count"] = len(r.json())
        except requests.RequestException:
            pass
        try:
            r = requests.get(f"{ORDER_SERVICE_URL}/api/orders/", timeout=3)
            if r.status_code == 200:
                data["orders_count"] = len(r.json())
        except requests.RequestException:
            pass
        return Response(data)
