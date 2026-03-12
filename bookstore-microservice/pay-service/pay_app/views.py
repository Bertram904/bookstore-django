from decimal import Decimal
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.openapi import AutoSchema

from .models import PaymentReservation


class PayReserve(APIView):
    schema = AutoSchema()

    """POST /api/pay/reserve/ {"order_id": "...", "amount": "99.00"} – FR4 Saga bước reserve thanh toán."""

    def post(self, request):
        order_id = request.data.get("order_id")
        amount = request.data.get("amount")
        if not order_id or amount is None:
            return Response({"error": "order_id and amount required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            amount = Decimal(str(amount))
        except Exception:
            return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)
        if PaymentReservation.objects.filter(order_id=order_id).exists():
            return Response({"error": "Already reserved"}, status=status.HTTP_400_BAD_REQUEST)
        obj = PaymentReservation.objects.create(order_id=order_id, amount=amount, status="reserved")
        return Response({"id": obj.id, "order_id": order_id, "status": "reserved"}, status=status.HTTP_201_CREATED)


class PayRelease(APIView):
    schema = AutoSchema()

    """POST /api/pay/<id>/release/ – Saga compensation khi order thất bại."""

    def post(self, request, pk):
        try:
            obj = PaymentReservation.objects.get(pk=pk)
        except PaymentReservation.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        if obj.status != "reserved":
            return Response({"error": "Not in reserved state"}, status=status.HTTP_400_BAD_REQUEST)
        obj.status = "released"
        obj.save(update_fields=["status"])
        return Response({"id": obj.id, "status": "released"})
