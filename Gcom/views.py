from django.shortcuts import render
from shop.models import Product,Brands

def home(request):
    products=Product.objects.all().filter(is_available=True).order_by('created_date')
    brands = Brands.objects.all()
    brands_cnt = len(brands)
    context={
        'products':products,
        'brands':brands,
        'brands_cnt':brands_cnt,
    }
    return render(request,'home.html',context)


