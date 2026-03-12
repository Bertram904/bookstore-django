from django.db import models


class PaymentReservation(models.Model):
    order_id = models.CharField(max_length=64, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, default="reserved")  # reserved, released, completed
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "pay_reservation"
