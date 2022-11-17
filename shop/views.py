from django.shortcuts import render,get_object_or_404,redirect
from django.db.models import Q
from django.core.paginator import EmptyPage, PageNotAnInteger,Paginator


from product_category.models import Product_category
from .models import Product,Review_Rating,Product_Gallery,Brands
from cart.models import Cart,Cart_Items
from .forms import ReviewForm

from django.contrib import messages
from cart.views import _cart_id
from django.core.files.storage import FileSystemStorage
# Create your views here.



def store(request,category_slug=None):

     if category_slug != None:
         categories=get_object_or_404(Product_category,slug=category_slug)
         products=Product.objects.filter(product_category=categories,is_available=True).order_by('id')
         paginator= Paginator(products,12)
         page = request.GET.get('page')
         paged_products = paginator.get_page(page)
         products_count = products.count()

     else:
         products=Product.objects.all().filter(is_available=True).order_by('id')
         paginator = Paginator(products, 12)
         page = request.GET.get('page')
         paged_products = paginator.get_page(page)
         products_count=products.count()

     all_categories=Product_category.objects.all()
     categories={}
     for category in all_categories:
        categories[category]=Product.objects.all().filter(product_category=category).count()


     context={
         'products':paged_products,
         'products_count':products_count,
         'categories':categories,

     }
     return render(request,'content.html',context)


def search(request):
    if 'key' in request.GET:
        key = request.GET['key']
        if key:
            products = Product.objects.all().filter(Q(product_description__icontains=key) | Q(product_name__icontains=key) )
            products_count=products.count()
    all_categories = Product_category.objects.all()
    categories = {}
    for category in all_categories:
        categories[category] = Product.objects.all().filter(product_category=category).count()

    context = {
            'products': products,
            'products_count': products_count,
            'categories': categories,

    }
    return render(request, 'content.html', context)


def product_detail(request,category_slug,product_slug):
    try:
        product=Product.objects.get(product_category__slug=category_slug,slug=product_slug)
        product_images=Product_Gallery.objects.filter(product__slug=product_slug)
        reviews = Review_Rating.objects.filter(product=product)
        avg_review = 0
        for review in reviews:
            avg_review += review.rating
        if len(reviews) > 0:
            avg_review = avg_review // len(reviews)
        else:
            avg_review = 0

        if request.user.is_authenticated:
            in_cart_item=Cart_Items.objects.filter(product=product,user=request.user).exists()
        else:
            in_cart_item = False

    except Exception as e:
        raise e
    context={
       'product':product,
       'product_images':product_images,
       'in_cart':in_cart_item,
       'reviews': reviews,
       'avg_review':avg_review,
       'int_avg_review':int(avg_review),
    }
    return render(request,"product_detail.html",context)

def submit_review(request,product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == "POST":
        try:
          review=Review_Rating.objects.get(user__id=request.user.id,product__id=product_id)
          form = ReviewForm(request.POST, instance=review)
          form.save()
          messages.success(request, 'Thank you! Your review has been updated.')
          return redirect(url)
        except:
            review_form = ReviewForm(request.POST,request.FILES)
            if review_form.is_valid():
                review_data=Review_Rating()
                review_data.subject=review_form.cleaned_data['subject']
                review_data.rating = review_form.cleaned_data['rating']
                review_data.review = review_form.cleaned_data['review']
                review_data.user_id=request.user.id
                if "reimage" in request.FILES:
                    imagetry = request.FILES['reimage']
                    fs = FileSystemStorage()
                    review_data.image = fs.save('photos/Review_image/'+str(product_id)+'/'+imagetry.name, imagetry)
                review_data.product_id=product_id
                review_data.ip=request.META.get('REMOTE_ADDR')
                review_data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
            else:
                messages.error(request, 'Error occurred while submitting')
                return redirect(url)
