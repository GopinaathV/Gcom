from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from .models import Cart,Cart_Items
from shop.models import Product,Variation
# Create your views here.

def _cart_id(request):
    cart=request.session.session_key
    if not cart:
        cart=request.session.create()
    return cart


def add_cart_items(request,product_id):
    product = Product.objects.get(id=product_id)
    if request.user.is_authenticated:
        variation_combo=[]
        if request.method=="POST":
            for item in request.POST:
                key=item
                value=request.POST[key]
                try:
                    variation = Variation.objects.get(product=product,variation_value__iexact=value)
                    variation_combo.append(variation)
                except:
                    pass

        current_user=request.user
        is_cart_item_exists = Cart_Items.objects.filter(product=product, user=current_user).exists()

        if is_cart_item_exists:
            cart_item = Cart_Items.objects.filter(product=product, user=current_user)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            if variation_combo in ex_var_list:
                index = ex_var_list.index(variation_combo)
                item_id = id[index]
                item = Cart_Items.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                item = Cart_Items.objects.create(product=product, quantity=1, user=current_user)
                if len(variation_combo) > 0:
                    item.variations.clear()
                    item.variations.add(*variation_combo)
                item.save()

        else:
            cart_item=Cart_Items.objects.create(product=product, quantity=1, user=current_user)
            if len(variation_combo) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*variation_combo)
            cart_item.save()
        return redirect('cart')
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart.save()

        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
            cart.save()

        if Cart_Items.objects.filter(cart=cart, product=product).exists():
            cart_item = Cart_Items.objects.get(cart=cart, product=product)
            cart_item.quantity += 1
            cart_item.save()
        else:
            cart_item = Cart_Items.objects.create(product=product, quantity=1, cart=cart)
            cart_item.save()

        return redirect('cart')


def remove_cart_items(request,product_id,cart_id):
    product=get_object_or_404(Product,id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = Cart_Items.objects.get(id=cart_id,product=product,user=request.user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = Cart_Items.objects.get(id=cart_id,product=product,cart=cart)
        if cart_item.quantity > 1:
            cart_item.quantity-=1
            cart_item.save()
        else:
            cart_item.delete()

    except:
        pass
    return redirect('cart')


def remove_all_items(request,product_id,cart_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = Cart_Items.objects.get(product=product, user=request.user, id=cart_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = Cart_Items.objects.get(product=product, cart=cart, id=cart_id)
    cart_item.delete()
    return redirect('cart')



def cart(request):
    cart_items=0
    tax=0
    total=0
    grand_total=0
    try:
        total=0
        if request.user.is_authenticated:
            cart_items=Cart_Items.objects.filter(user=request.user,is_active=True)
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=Cart_Items.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total+=(cart_item.product.product_price)*(cart_item.quantity)
        tax=total*0.18
        grand_total=total+tax
    except ObjectDoesNotExist:
        pass
    context={
       'cart_items':cart_items,
       'total':total,
       'tax':tax,
       'grand_total':grand_total
    }
    return render(request,"cart.html",context)

@login_required(login_url='login')
def checkout(request):
    cart_items=0
    tax=0
    total=0
    grand_total=0
    try:
        total=0
        current_user=request.user
        if request.user.is_authenticated:
            cart_items=Cart_Items.objects.filter(user=request.user,is_active=True)

        for cart_item in cart_items:
            total+=(cart_item.product.product_price)*(cart_item.quantity)
        tax=total*0.18
        grand_total=total+tax
    except ObjectDoesNotExist:
        pass
    context={
       'cart_items':cart_items,
       'total':total,
       'user':current_user,
       'tax':tax,
       'grand_total':grand_total
    }
    return render(request,"Checkout.html",context)


