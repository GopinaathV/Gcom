from django.contrib import admin
from django.urls import path,include

from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('delivery/<int:order_id>', views.delivery, name='delivery'),
    path('logout/', views.logout, name='logout'),
    path('activation/<uidb64>/<token>/', views.email_activation, name='email_activation'),
    path('pwd_activation/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('forgot_pwd/', views.forgot_pwd, name='forgot_pwd'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),

]