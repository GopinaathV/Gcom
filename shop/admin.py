from django.contrib import admin
from .models import Product,Review_Rating,Product_Gallery,Brands,Variation
# Register your models here.


class Product_Admin(admin.ModelAdmin):
    list_display = ('product_name', 'product_price', 'stock', 'product_category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}

class Review_Admin(admin.ModelAdmin):
    list_display = ('product', 'user', 'review', 'rating', 'status', 'created_at')
    list_filter = ('user','product',)

class Product_Gallery_Admin(admin.ModelAdmin):
    list_display = ('product',)

class Brands_Admin(admin.ModelAdmin):
    list_display = ('name',)

class Variation_Admin(admin.ModelAdmin):
    list_display = ('variation_value','product','variation_category')


admin.site.register(Review_Rating,Review_Admin)
admin.site.register(Product,Product_Admin)
admin.site.register(Product_Gallery,Product_Gallery_Admin)
admin.site.register(Brands,Brands_Admin)
admin.site.register(Variation,Variation_Admin)

