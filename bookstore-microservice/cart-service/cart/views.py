import os
import requests
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.openapi import AutoSchema

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

CUSTOMER_SERVICE_URL = os.environ.get("CUSTOMER_SERVICE_URL", "http://customer-service:8000")
BOOK_SERVICE_URL = os.environ.get("BOOK_SERVICE_URL", "http://book-service:8000")


def _customer_exists(customer_id):
    try:
        r = requests.get(f"{CUSTOMER_SERVICE_URL}/api/customers/{customer_id}/", timeout=3)
        return r.status_code == 200
    except requests.RequestException:
        return False


def _book_exists(book_id):
    try:
        r = requests.get(f"{BOOK_SERVICE_URL}/api/books/{book_id}/", timeout=3)
        return r.status_code == 200
    except requests.RequestException:
        return False


def _get_books_batch(book_ids):
    if not book_ids:
        return {}
    try:
        ids_param = "&".join(f"ids={i}" for i in book_ids)
        r = requests.get(f"{BOOK_SERVICE_URL}/api/books/batch/?{ids_param}", timeout=5)
        if r.status_code != 200:
            return {}
        return {b["id"]: b for b in r.json()}
    except requests.RequestException:
        return {}


class CartCreate(APIView):
    schema = AutoSchema()
    serializer_class = CartSerializer

    """POST /api/cart/create/ {"customer_id": 1} – được gọi bởi customer-service khi đăng ký (FR1)."""

    def post(self, request):
        customer_id = request.data.get("customer_id")
        if customer_id is None:
            return Response({"error": "customer_id required"}, status=status.HTTP_400_BAD_REQUEST)
        if not _customer_exists(customer_id):
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        if Cart.objects.filter(customer_id=customer_id).exists():
            return Response({"error": "Cart already exists"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CartSerializer(data={"customer_id": customer_id})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartAdd(APIView):
    schema = AutoSchema()
    serializer_class = CartItemSerializer

    """POST /api/cart/add/<customer_id>/ {"book_id": 1, "quantity": 2} – thêm hoặc cập nhật mục (FR3)."""

    def post(self, request, customer_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        book_id = request.data.get("book_id")
        quantity = request.data.get("quantity", 1)
        if book_id is None:
            return Response({"error": "book_id required"}, status=status.HTTP_400_BAD_REQUEST)
        if not _book_exists(book_id):
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        item, created = CartItem.objects.get_or_create(cart=cart, book_id=book_id, defaults={"quantity": quantity})
        if not created:
            item.quantity += quantity
            item.save(update_fields=["quantity"])
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class CartView(APIView):
    schema = AutoSchema()

    """GET /api/cart/view/<customer_id>/ – xem giỏ kèm thông tin sách từ book-service (FR3)."""

    def get(self, request, customer_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        items = list(cart.items.all())
        book_ids = [i.book_id for i in items]
        books_map = _get_books_batch(book_ids)
        result = []
        for item in items:
            book_info = books_map.get(item.book_id, {})
            result.append({
                "id": item.id,
                "book_id": item.book_id,
                "quantity": item.quantity,
                "title": book_info.get("title"),
                "author": book_info.get("author"),
                "price": str(book_info.get("price")) if book_info.get("price") is not None else None,
            })
        return Response({"cart_id": cart.id, "customer_id": customer_id, "items": result})


class CartUpdate(APIView):
    schema = AutoSchema()
    serializer_class = CartItemSerializer

    """PATCH /api/cart/update/<customer_id>/<item_id>/ {"quantity": 3} (FR3)."""

    def patch(self, request, customer_id, item_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
            item = cart.items.get(pk=item_id)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response({"error": "Cart or item not found"}, status=status.HTTP_404_NOT_FOUND)
        quantity = request.data.get("quantity")
        if quantity is not None:
            if quantity < 1:
                item.delete()
                return Response({"status": "removed"}, status=status.HTTP_200_OK)
            item.quantity = quantity
            item.save(update_fields=["quantity"])
        return Response(CartItemSerializer(item).data)


class CartRemove(APIView):
    schema = AutoSchema()

    """DELETE /api/cart/remove/<customer_id>/<item_id>/ (FR3)."""

    def delete(self, request, customer_id, item_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
            item = cart.items.get(pk=item_id)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response({"error": "Cart or item not found"}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartGetByCustomer(APIView):
    schema = AutoSchema()

    """GET /api/cart/by-customer/<customer_id>/ – trả về cart + items (cho order-service)."""

    def get(self, request, customer_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        items = [{"book_id": i.book_id, "quantity": i.quantity} for i in cart.items.all()]
        return Response({"cart_id": cart.id, "customer_id": customer_id, "items": items})
