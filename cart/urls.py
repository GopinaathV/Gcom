from django.urls import path
from . import views


urlpatterns = [
    path('', views.cart, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_cart_items, name='add_cart_items'),
    path('remove_from_cart/<int:product_id>/<int:cart_id>', views.remove_cart_items, name='remove_cart_items'),
    path('remove_all_items/<int:product_id>/<int:cart_id>', views.remove_all_items, name='remove_all_items'),
    path('checkout/', views.checkout, name='checkout'),
]