from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "author", "price", "stock", "created_at"]
    list_filter = ["author"]
    search_fields = ["title", "author"]
