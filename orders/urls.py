from django.urls import path
from . import views


urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('create-checkout-session/', views.create_checkout_session, name='checkout_final'),
    path('success/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),

]