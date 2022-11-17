

from .models import Cart,Cart_Items
from .views import _cart_id

def cart_items_count(request):
    cart_cnt=0
    if request.path=='admin':
        return {}
    else:
       try:
            cart_cnt=0
            if request.user.is_authenticated:
                cart_items=Cart_Items.objects.all().filter(user=request.user)
            else:
                cart=Cart.objects.filter(cart_id=_cart_id(request))
                cart_items=Cart_Items.objects.all().filter(cart=cart[:1])
            for cart_item in cart_items:
                cart_cnt += cart_item.quantity

       except Cart.DoesNotExist:
           cart_cnt=0

    return dict(cart_cnt=cart_cnt)



