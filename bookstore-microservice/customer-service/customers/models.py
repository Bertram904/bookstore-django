from django.db import models


class Customer(models.Model):
    """Khách hàng – database riêng của customer-service (Database per Service)."""
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "customers_customer"

    def __str__(self):
        return self.email
