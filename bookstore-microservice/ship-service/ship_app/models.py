from django.db import models


class ShipmentReservation(models.Model):
    order_id = models.CharField(max_length=64, unique=True)
    address = models.CharField(max_length=512, blank=True)
    shipper = models.CharField(max_length=64, blank=True, null=True)
    status = models.CharField(max_length=20, default="reserved")  # reserved, released, shipped
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ship_reservation"
