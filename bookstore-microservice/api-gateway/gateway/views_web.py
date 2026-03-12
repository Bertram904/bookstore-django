from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
@require_GET
def home(request):
    return render(request, "index.html")


@ensure_csrf_cookie
@require_GET
def cart_page(request, customer_id=None):
    return render(request, "cart.html", {"customer_id": customer_id or ""})


@ensure_csrf_cookie
@require_GET
def checkout_page(request):
    return render(request, "checkout.html")


@ensure_csrf_cookie
@require_GET
def staff_page(request):
    return render(request, "staff.html")


@ensure_csrf_cookie
@require_GET
def manager_page(request):
    return render(request, "manager.html")


@ensure_csrf_cookie
@require_GET
def admin_center_page(request):
    return render(request, "admin_center.html")


@ensure_csrf_cookie
@require_GET
def login_page(request):
    return render(request, "login.html")


@ensure_csrf_cookie
@require_GET
def register_page(request):
    return render(request, "register.html")


@ensure_csrf_cookie
@require_GET
def logout_page(request):
    return render(request, "logout.html")


@ensure_csrf_cookie
@require_GET
def book_detail_page(request, book_id):
    return render(request, "book.html", {"book_id": book_id})
