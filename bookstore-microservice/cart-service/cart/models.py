from django.db import models


class Cart(models.Model):
    """Giỏ hàng – chỉ lưu customer_id (ID tham chiếu), không FK sang customer-service."""
    customer_id = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cart_cart"


class CartItem(models.Model):
    """Mục trong giỏ – book_id là ID tham chiếu tới book-service."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    book_id = models.IntegerField()
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "cart_cartitem"
        unique_together = [["cart", "book_id"]]
