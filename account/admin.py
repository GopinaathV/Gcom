from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register your models here.

class Account_Admin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'user_name', 'last_login', 'date_joined', 'is_active','is_admin',)
    list_display_links = ('email', 'first_name',)
    readonly_fields = ('last_login', 'date_joined','is_admin','is_staff','is_superadmin')
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()



admin.site.register(Account,Account_Admin)



