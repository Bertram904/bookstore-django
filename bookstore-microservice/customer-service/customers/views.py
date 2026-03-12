import logging
import os
import requests
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.openapi import AutoSchema

from .models import Customer
from .serializers import CustomerSerializer

logger = logging.getLogger(__name__)
CART_SERVICE_URL = os.environ.get("CART_SERVICE_URL", "http://cart-service:8000")


class CustomerListCreate(APIView):
    schema = AutoSchema()
    serializer_class = CustomerSerializer

    """GET: Danh sách khách hàng. POST: Đăng ký – sau khi tạo customer gọi cart-service tạo giỏ (FR1)."""

    def get(self, request):
        customers = Customer.objects.all().order_by("-created_at")
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        customer = serializer.save()
        # FR1: Tự động tạo cart khi đăng ký – gọi cart-service qua REST
        try:
            r = requests.post(
                f"{CART_SERVICE_URL}/api/cart/create/",
                json={"customer_id": customer.id},
                timeout=5,
            )
            if r.status_code not in (200, 201):
                logger.warning("Cart creation returned %s: %s", r.status_code, r.text)
        except requests.RequestException as e:
            logger.exception("Failed to create cart for customer %s: %s", customer.id, e)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CustomerDetail(APIView):
    schema = AutoSchema()
    serializer_class = CustomerSerializer

    """GET /api/customers/<id>/ – dùng cho các service khác validate customer_id."""

    def get(self, request, pk):
        try:
            customer = Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)
