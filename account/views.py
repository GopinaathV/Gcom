from django.shortcuts import render,redirect,get_object_or_404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from .models import Account
from cart.models import Cart_Items
from orders.models import OrderProduct,Order,Payment
from .forms import RegistrationForm,AccountForm

import boto3
from botocore.exceptions import ClientError

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_no = form.cleaned_data['phone_no']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email,
                                               user_name=username, password=password)
            user.phone_number = phone_no
            user.save()
            # User Activation using email
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            client = boto3.client('ses', region_name=settings.AWS_REGION,
                                  aws_access_key_id=settings.AWS_PUBLIC_KEY,
                                  aws_secret_access_key=settings.AWS_PRIVATE_KEY)
            to_email = email
            BODY_TEXT = ("Amazon SES Test (Python)\r\n"
                         "This email was sent with Amazon SES using the "
                         "AWS SDK for Python (Boto)."
                         )
            message = render_to_string('Account/Activation_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            try:
                # Provide the contents of the email.
                response = client.send_email(
                    Destination={
                        'ToAddresses': [
                            to_email,
                        ],
                    },
                    Message={
                        'Body': {
                        'Html': {
                        'Charset': settings.CHARSET,
                        'Data': message,
                        },
                        'Text': {
                        'Charset': settings.CHARSET,
                        'Data': BODY_TEXT,
                        },
                        },
                        'Subject': {
                        'Charset': settings.CHARSET,
                        'Data': mail_subject,
                        },
                    },
                    Source=settings.SENDER,
                )
            except ClientError as e:
                print(e.response['Error']['Message'])
            else:
                print("Email sent! Message ID:"),
                print(response['MessageId'])

            return redirect('/account/login')

    else:
        form = RegistrationForm()

    context={
        'form':form,
    }
    return render(request,'Account/register.html',context)

def login(request):
    if request.method=="POST":
        email=request.POST['email']
        password=request.POST['password']
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, 'Successfully logged in!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials!!')
            return redirect('login')
    else:
        return render(request,'Account/login.html')


def email_activation(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user=None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')


@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')

@login_required(login_url = 'login')
def dashboard(request):

    cart_items = Cart_Items.objects.filter(user=request.user)
    orders = OrderProduct.objects.filter(user=request.user)
    orders_cnt=len(orders)
    cart_cnt=len(cart_items)
    context={
        'orders':orders,
        'orders_cnt':orders_cnt,
        'cart_cnt':cart_cnt,
    }
    return render(request,"Account/Dashboard.html",context)


def forgot_pwd(request):
    if request.method == "POST":
        user_email=request.POST['email']
        if Account.objects.filter(email=user_email).exists():
            user=Account.objects.get(email__exact=user_email)
            current_site=get_current_site(request)
            message = render_to_string('Account/resetPassword.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            return HttpResponse(message)

        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')

    return render(request,'Account/Forgot_password.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'Account/cnf_resetPassword.html')

@login_required(login_url = 'login')
def edit_profile(request):
    userprofile = get_object_or_404(Account, user_name=request.user.user_name)
    if request.method == 'POST':
        profile_form = AccountForm(request.POST, request.FILES, instance=userprofile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        profile_form = AccountForm(instance=userprofile)
    context = {
        'user_profile': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'Account/Account_general.html', context)

@login_required(login_url = 'login')
def change_password(request):
   if request.method == "POST":
       current_pwd=request.POST['Current_password']
       new_pwd=request.POST['New_password']
       confirm_pwd=request.POST['Confirm_password']
       user = Account.objects.get(user_name__exact=request.user.user_name)

       if new_pwd == confirm_pwd:
           success = user.check_password(current_pwd)
           if success:
               user.set_password(new_pwd)
               user.save()
               messages.success(request, 'Password updated successfully.')
               return redirect('change_password')
           else:
               messages.error(request, 'Please enter valid current password')
               return redirect('change_password')
       else:
           messages.error(request, 'Password does not match!')
           return redirect('change_password')

   return render(request, 'Account/Change_password.html')


def delivery(request,order_id):
    order=Order.objects.get(order_number=order_id)
    order_status = False
    payment_status= False
    out_for_delivery = False
    delivered=False
    if order.status=="Accepted":
        order_status=True
        payment=Payment.objects.get(id=order.payment.id)
        if payment.status=="Success":
            payment_status = True

    context={
        'order_status':order_status,
    'payment_status':payment_status,
    'out_for_delivery':out_for_delivery,
    'delivered':delivered
    }
    return render(request, 'Account/Delivery_progress.html',context)
