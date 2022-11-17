from django.shortcuts import render,redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse,HttpResponse

from shop.models import Product
from cart.models import Cart_Items
from .models import Order,Payment,OrderProduct
from .forms import OrderForm

import datetime
import stripe
import json

# Create your views here.

stripe.api_key = settings.STRIPE_PRIVATE_KEY

def place_order(request):
    current_user = request.user
    cart_items = Cart_Items.objects.filter(user=current_user)
    cart_count = cart_items.count()
    total = 0
    quantity = 0
    grand_total = 0
    tax = 0
    if cart_count <= 0:
        return redirect('store')

    for cart_item in cart_items:
        total += (cart_item.product.product_price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (18 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line = form.cleaned_data['address_line']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")  # 20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'Payment.html', context)
    else:
        return redirect('checkout')

@csrf_exempt
def create_checkout_session(request):
    body = json.loads(request.body)
    current_user = request.user
    cart_items = Cart_Items.objects.filter(user=current_user)
    cart_count = cart_items.count()
    total = 0
    quantity = 0
    grand_total = 0
    tax = 0
    if cart_count <= 0:
        return redirect('store')

    for cart_item in cart_items:
        total += (cart_item.product.product_price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (18 * total) / 100
    grand_total = total + tax

    session = stripe.checkout.Session.create(
    client_reference_id=request.user.id if request.user.is_authenticated else None,
    payment_method_types=['card'],
    line_items=[{
      'price_data': {
        'currency': 'inr',
        'product_data': {
          'name': 'Gcom',
        },
        'unit_amount': int(grand_total*100),
      },
      'quantity': 1,
    }],
    # metadata={
    #         "order_id": order.id
    #     },
    mode='payment',
    success_url="http://127.0.0.1:8000/order/success?order_no="+str(body['orderID'])+"&session_no={CHECKOUT_SESSION_ID}",
    cancel_url = "http://127.0.0.1:8000/order/cancel?order_no="+str(body['orderID'])+"&session_no={CHECKOUT_SESSION_ID}"
    )

    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
    payment = Payment(
        user=request.user,
        payment_id=session.id,
        payment_method="Stripe",
        amount_paid=order.order_total,
        status=body['status'],
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()

    cart_items = Cart_Items.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.product_price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = Cart_Items.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

    return JsonResponse({'id': session.id})


def success(request):
    payment_id=request.GET.get('session_no')
    order_id = request.GET.get('order_no')
    cart_items = Cart_Items.objects.filter(user=request.user)

    for item in cart_items:
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()
    Cart_Items.objects.filter(user=request.user).delete()
    try:
        order=Order.objects.get(order_number=order_id, is_ordered=True)
        order.status="Accepted"
        order.save()
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        tax =0
        grand_total=0
        for product in ordered_products:

            subtotal += product.product_price * product.quantity

        product_status = Payment.objects.get(payment_id=payment_id)
        product_status.status = "Success"
        product_status.save()
        tax=(18/100)*subtotal
        grand_total=subtotal+tax
        context={
            'total':subtotal,
            'tax':tax,
             'grand_total':grand_total,
            'ordered_products':ordered_products,
        }
        return render(request, 'Payment_success.html',context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
            product_status = Payment.objects.get(payment_id=payment_id)
            product_status.status = "Fail"
            product_status.save()
            return redirect('cart')



def cancel(request):
    payment_id = request.GET['session_id']
    product_status = Payment.objects.get(payment_id=payment_id)
    product_status.status = "Fail"
    product_status.save()
    return render(request,'Payment_rejected.html')