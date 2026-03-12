from django.db import models
from decimal import Decimal


class Order(models.Model):
    STATUS_CHOICES = [("pending", "Pending"), ("completed", "Completed"), ("failed", "Failed")]
    customer_id = models.IntegerField()
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_reservation_id = models.IntegerField(null=True, blank=True)
    ship_reservation_id = models.IntegerField(null=True, blank=True)
    shipper = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order_order"
