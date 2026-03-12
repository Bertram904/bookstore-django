from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.openapi import AutoSchema

from .models import ShipmentReservation


class ShipReserve(APIView):
    schema = AutoSchema()

    """POST /api/ship/reserve/ {"order_id": "...", "address": "..."} – FR4 Saga."""

    def post(self, request):
        order_id = request.data.get("order_id")
        address = request.data.get("address", "")
        if not order_id:
            return Response({"error": "order_id required"}, status=status.HTTP_400_BAD_REQUEST)
        if ShipmentReservation.objects.filter(order_id=order_id).exists():
            return Response({"error": "Already reserved"}, status=status.HTTP_400_BAD_REQUEST)
        shipper = request.data.get("shipper", "")
        obj = ShipmentReservation.objects.create(order_id=order_id, address=address, shipper=shipper, status="reserved")
        return Response({"id": obj.id, "order_id": order_id, "status": "reserved", "shipper": shipper}, status=status.HTTP_201_CREATED)


class ShipRelease(APIView):
    schema = AutoSchema()

    """POST /api/ship/<id>/release/ – Saga compensation."""

    def post(self, request, pk):
        try:
            obj = ShipmentReservation.objects.get(pk=pk)
        except ShipmentReservation.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        if obj.status != "reserved":
            return Response({"error": "Not in reserved state"}, status=status.HTTP_400_BAD_REQUEST)
        obj.status = "released"
        obj.save(update_fields=["status"])
        return Response({"id": obj.id, "status": "released"})


class ShipOptions(APIView):
    schema = AutoSchema()

    """GET /api/ship/shippers/ – danh sách đơn vị giao hàng."""

    def get(self, request):
        shippers = [
            {"id": "fastship", "name": "FastShip (Nhanh)"},
            {"id": "standard", "name": "Standard Express"},
            {"id": "green", "name": "Green Delivery (Tiết kiệm)"},
        ]
        return Response(shippers)
