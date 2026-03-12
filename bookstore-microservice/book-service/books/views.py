from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.openapi import AutoSchema

from .models import Book
from .serializers import BookSerializer


class BookListCreate(APIView):
    schema = AutoSchema()
    serializer_class = BookSerializer

    def get(self, request):
        books = Book.objects.all().order_by("id")
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BookDetail(APIView):
    schema = AutoSchema()
    serializer_class = BookSerializer

    def get(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(BookSerializer(book).data)

    def put(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = BookSerializer(book, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookBatch(APIView):
    schema = AutoSchema()
    serializer_class = BookSerializer

    """GET /api/books/batch/?ids=1&ids=2 – dùng cho cart-service lấy thông tin sách theo lô."""

    def get(self, request):
        ids = request.query_params.getlist("ids", [])
        if not ids:
            return Response([])
        try:
            ids = [int(i) for i in ids]
        except ValueError:
            return Response({"error": "Invalid ids"}, status=status.HTTP_400_BAD_REQUEST)
        books = Book.objects.filter(id__in=ids)
        return Response(BookSerializer(books, many=True).data)
