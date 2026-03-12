import os
import uuid
import requests
from decimal import Decimal
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.openapi import AutoSchema

from .models import Order

CART_SERVICE_URL = os.environ.get("CART_SERVICE_URL", "http://cart-service:8000")
PAY_SERVICE_URL = os.environ.get("PAY_SERVICE_URL", "http://pay-service:8000")
SHIP_SERVICE_URL = os.environ.get("SHIP_SERVICE_URL", "http://ship-service:8000")
BOOK_SERVICE_URL = os.environ.get("BOOK_SERVICE_URL", "http://book-service:8000")


def _get_cart(customer_id):
    try:
        r = requests.get(f"{CART_SERVICE_URL}/api/cart/by-customer/{customer_id}/", timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except requests.RequestException:
        return None


def _get_book_prices(book_ids):
    if not book_ids:
        return {}
    try:
        ids_param = "&".join(f"ids={i}" for i in book_ids)
        r = requests.get(f"{BOOK_SERVICE_URL}/api/books/batch/?{ids_param}", timeout=5)
        if r.status_code != 200:
            return {}
        return {b["id"]: Decimal(str(b["price"])) for b in r.json()}
    except requests.RequestException:
        return {}


class OrderCreate(APIView):
    schema = AutoSchema()

    """
    FR4: Tạo đơn hàng với Saga đơn giản:
    1. Lấy giỏ từ cart-service, tính tổng từ book-service
    2. Tạo Order status=pending
    3. Reserve payment -> reserve shipping
    4. Nếu thành công: status=completed. Nếu thất bại: compensate (release pay, release ship), status=failed
    """

    def post(self, request):
        customer_id = request.data.get("customer_id")
        address = request.data.get("address", "")
        if customer_id is None:
            return Response({"error": "customer_id required"}, status=status.HTTP_400_BAD_REQUEST)

        cart_data = _get_cart(customer_id)
        if not cart_data or not cart_data.get("items"):
            return Response({"error": "Cart not found or empty"}, status=status.HTTP_400_BAD_REQUEST)

        book_ids = list({i["book_id"] for i in cart_data["items"]})
        prices = _get_book_prices(book_ids)
        total = Decimal("0")
        for item in cart_data["items"]:
            price = prices.get(item["book_id"])
            if price is not None:
                total += price * item["quantity"]

        order_id = str(uuid.uuid4())
        order = Order.objects.create(
            customer_id=customer_id,
            total=total,
            status="pending",
            payment_reservation_id=None,
            ship_reservation_id=None,
            shipper=request.data.get("shipper", ""),
        )

        pay_reservation_id = None
        ship_reservation_id = None

        try:
            # Bước 2: Reserve payment
            r_pay = requests.post(
                f"{PAY_SERVICE_URL}/api/pay/reserve/",
                json={"order_id": order_id, "amount": str(total)},
                timeout=5,
            )
            if r_pay.status_code not in (200, 201):
                raise Exception(f"Pay reserve failed: {r_pay.text}")
            pay_reservation_id = r_pay.json().get("id")
            order.payment_reservation_id = pay_reservation_id
            order.save(update_fields=["payment_reservation_id"])

            # Bước 3: Reserve shipping
            r_ship = requests.post(
                f"{SHIP_SERVICE_URL}/api/ship/reserve/",
                json={"order_id": order_id, "address": address},
                timeout=5,
            )
            if r_ship.status_code not in (200, 201):
                raise Exception(f"Ship reserve failed: {r_ship.text}")
            ship_reservation_id = r_ship.json().get("id")
            order.ship_reservation_id = ship_reservation_id
            order.save(update_fields=["ship_reservation_id"])

            # Bước 4: Confirm
            order.status = "completed"
            order.save(update_fields=["status"])
            return Response({
                "id": order.id,
                "customer_id": order.customer_id,
                "total": str(order.total),
                "status": order.status,
                "payment_reservation_id": pay_reservation_id,
                "ship_reservation_id": ship_reservation_id,
                "shipper": order.shipper,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Compensation: release pay, release ship
            if pay_reservation_id:
                try:
                    requests.post(f"{PAY_SERVICE_URL}/api/pay/{pay_reservation_id}/release/", timeout=3)
                except requests.RequestException:
                    pass
            if ship_reservation_id:
                try:
                    requests.post(f"{SHIP_SERVICE_URL}/api/ship/{ship_reservation_id}/release/", timeout=3)
                except requests.RequestException:
                    pass
            order.status = "failed"
            order.save(update_fields=["status"])
            return Response({"error": str(e), "order_id": order.id, "status": "failed"}, status=status.HTTP_502_BAD_GATEWAY)


class OrderList(APIView):
    schema = AutoSchema()

    def get(self, request):
        customer_id = request.query_params.get("customer_id")
        if customer_id:
            try:
                customer_id = int(customer_id)
                orders = Order.objects.filter(customer_id=customer_id).order_by("-created_at")
            except ValueError:
                return Response({"error": "Invalid customer_id"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            orders = Order.objects.all().order_by("-created_at")
        data = [{"id": o.id, "customer_id": o.customer_id, "total": str(o.total), "status": o.status, "created_at": o.created_at.isoformat()} for o in orders]
        return Response(data)
