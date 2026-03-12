from django.urls import path
from .views import CartCreate, CartAdd, CartView, CartUpdate, CartRemove, CartGetByCustomer

urlpatterns = [
    path("cart/create/", CartCreate.as_view()),
    path("cart/add/<int:customer_id>/", CartAdd.as_view()),
    path("cart/view/<int:customer_id>/", CartView.as_view()),
    path("cart/update/<int:customer_id>/<int:item_id>/", CartUpdate.as_view()),
    path("cart/remove/<int:customer_id>/<int:item_id>/", CartRemove.as_view()),
    path("cart/by-customer/<int:customer_id>/", CartGetByCustomer.as_view()),
]
