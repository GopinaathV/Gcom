from django.contrib import admin
from .models import Product_category
# Register your models here.


class Category_Admin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('category_name',)}
    list_display = ('category_name', 'slug')


admin.site.register(Product_category,Category_Admin)
