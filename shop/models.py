from django.db import models
from product_category.models import Product_category
from account.models import Account

from django.urls import reverse
import os
from django.conf import settings


def gallery_path(instance,filename):
    product_name='product_gallery/{0}/{1}'.format(instance.product.id,filename)
    full_path=os.path.join(settings.MEDIA_ROOT,product_name)
    if os.path.exists(full_path):
        os.remove(full_path)
    return product_name

class Brands(models.Model):
    name = models.CharField(max_length=200, unique=True)
    image = models.ImageField(upload_to='photos/Brands', blank=True)
    url = models.URLField(max_length=300, blank=True)

    def __str__(self):
        return self.name

    def product_total(self):
        products=Product.objects.filter(brand__id=self.id)
        return len(products)

# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    product_description = models.TextField(max_length=500, blank=True)
    product_price = models.IntegerField()
    product_images = models.ImageField(upload_to='photos/products')
    product_category = models.ForeignKey(Product_category, on_delete=models.CASCADE)
    brand=models.ForeignKey(Brands, on_delete=models.CASCADE,null=True)
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_detail',args=[self.product_category.slug,self.slug])

    def product_rating(self):
        reviews=Review_Rating.objects.filter(product=self.id)
        avg=0
        for review in reviews:
            avg+=review.rating
        if avg>0:
            avg=avg//len(reviews)
        return int(avg)

    def total_reviews(self):
        reviews=Review_Rating.objects.filter(product=self.id)
        return len(reviews)

class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)

    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)

variation_category_choice = (
    ('color', 'color'),
    ('size', 'size'),
)

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    variation_value= models.CharField(max_length=100)
    is_active= models.BooleanField(default=True)
    created_date= models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value




class Product_Gallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image=models.ImageField(upload_to=gallery_path, blank=True)


class Review_Rating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    image=models.ImageField(upload_to='photos/Review_image', blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject













