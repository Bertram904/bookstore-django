from django.urls import path, re_path
from .views import ProxyView
from .views_web import home, cart_page, checkout_page, staff_page, manager_page, admin_center_page, login_page, register_page, logout_page, book_detail_page

# API Gateway: /api/customers/... -> customer-service, /api/books/... -> book-service, ...
# Path prefix được giữ nguyên khi forward (service đã có /api/ trong urlconf)

class CustomerProxy(ProxyView):
    service_key = "customer"

class StaffProxy(ProxyView):
    service_key = "staff"

class ManagerProxy(ProxyView):
    service_key = "manager"

class CatalogProxy(ProxyView):
    service_key = "catalog"

class BookProxy(ProxyView):
    service_key = "book"

class CartProxy(ProxyView):
    service_key = "cart"

class OrderProxy(ProxyView):
    service_key = "order"

class ShipProxy(ProxyView):
    service_key = "ship"

class PayProxy(ProxyView):
    service_key = "pay"

class CommentProxy(ProxyView):
    service_key = "comment"

class RecommenderProxy(ProxyView):
    service_key = "recommender"

urlpatterns = [
    path("", home),
    path("login/", login_page),
    path("register/", register_page),
    path("logout/", logout_page),
    path("cart/", cart_page),
    path("cart/<int:customer_id>/", cart_page),
    path("checkout/", checkout_page),
    path("staff/", staff_page),
    path("manager/", manager_page),
    path("admin-center/", admin_center_page),
    path("book/<int:book_id>/", book_detail_page),
    path("api/customers/", CustomerProxy.as_view(), {"path": "api/customers/"}),
    re_path(r"^api/customers/(?P<path>.*)$", CustomerProxy.as_view()),
    path("api/staff/", StaffProxy.as_view(), {"path": "api/staff/"}),
    re_path(r"^api/staff/(?P<path>.*)$", StaffProxy.as_view()),
    path("api/manager/", ManagerProxy.as_view(), {"path": "api/manager/"}),
    re_path(r"^api/manager/(?P<path>.*)$", ManagerProxy.as_view()),
    path("api/catalog/", CatalogProxy.as_view(), {"path": "api/catalog/"}),
    re_path(r"^api/catalog/(?P<path>.*)$", CatalogProxy.as_view()),
    path("api/books/", BookProxy.as_view(), {"path": "api/books/"}),
    re_path(r"^api/books/(?P<path>.*)$", BookProxy.as_view()),
    path("api/cart/", CartProxy.as_view(), {"path": "api/cart/"}),
    re_path(r"^api/cart/(?P<path>.*)$", CartProxy.as_view()),
    path("api/orders/", OrderProxy.as_view(), {"path": "api/orders/"}),
    re_path(r"^api/orders/(?P<path>.*)$", OrderProxy.as_view()),
    path("api/ship/", ShipProxy.as_view(), {"path": "api/ship/"}),
    re_path(r"^api/ship/(?P<path>.*)$", ShipProxy.as_view()),
    path("api/pay/", PayProxy.as_view(), {"path": "api/pay/"}),
    re_path(r"^api/pay/(?P<path>.*)$", PayProxy.as_view()),
    path("api/reviews/", CommentProxy.as_view(), {"path": "api/reviews/"}),
    re_path(r"^api/reviews/(?P<path>.*)$", CommentProxy.as_view()),
    path("api/recommend/", RecommenderProxy.as_view(), {"path": "api/recommend/"}),
    re_path(r"^api/recommend/(?P<path>.*)$", RecommenderProxy.as_view()),
]
