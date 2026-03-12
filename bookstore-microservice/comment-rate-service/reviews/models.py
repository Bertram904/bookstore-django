from django.db import models


class Review(models.Model):
    book_id = models.IntegerField()  # ID tham chiếu tới book-service
    customer_id = models.IntegerField()
    rating = models.PositiveSmallIntegerField()  # 1-5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reviews_review"
        unique_together = [["book_id", "customer_id"]]
