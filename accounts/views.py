from django.contrib import messages, auth
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from accounts.forms import RegistrationForm, UserForm, UserProfileForm
from accounts.models import Account, UserProfile

#Verification by email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator

from carts.models import Cart, CartItem
from carts.views import _cart_id
import requests

from orders.models import Order, OrderProduct
# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name'].strip()# this removes any extra spaces from the first name
            last_name = form.cleaned_data['last_name'].strip()
            email = form.cleaned_data['email'].strip()
            phone_number = form.cleaned_data['phone_number'].strip()
            password = form.cleaned_data['password'].strip()
            username = email.split('@')[0]
            
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email,  username=username, password=password)
            user.phone_number = phone_number
            user.save()

            # USER ACTIVATION by email
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)), # encoding the user id
                'token': default_token_generator.make_token(user), # generating token for user activation
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            #messages.success(request, 'Thank you for registering with us. We have sent you a verification email to your email address. Please verify to activate your account.')
            return redirect('/accounts/login/?command=verification&email='+email)# redirecting to login page with a message to verify email

    else: 
        form = RegistrationForm() 
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context )    

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']


        user = auth.authenticate(request, email=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request)) #get the cart using the card_id present in the session
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    
                    #Getting the product variations by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # get the cart items from the user to access his product variations
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    #product_variation = [1,2,3,4,5,6]
                    #ex_var_list = [4,6,3,5]

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity +=1 # increase the cart item quantity
                            item.user = user #assign the user to the cart item
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart = cart)
                            for item in cart_item:
                                item.user = user #assign the user to the cart item
                                item.save()
                                        
            except:
                pass
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            url = request.META.get('HTTP_REFERER') # get the previous url
            try:
                query = requests.utils.urlparse(url).query #get the query parameter
                #next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))#split the query parameter
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)  
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')

def activate(request, uidb64, token): # This function will be called when user clicks on the activation link
    try:
        uid = urlsafe_base64_decode(uidb64).decode() # decoding the user id
        user = Account._default_manager.get(pk=uid) # getting the user from the database
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token): # checking if the token is valid
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')
    
@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id = request.user.id, is_ordered=True)
    orders_count = orders.count()
    userprofile = UserProfile.objects.get(user_id=request.user.id)
    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/dashboard.html', context)

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)# exact match of email exact is case sensitive and iexat is case insensitive
            # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user), 
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, f'Password reset email has been sent to {email}.') 
            return redirect('login')

        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')

def resetpassword_validate(request, uidb64, token): # This function will be called when user clicks on the reset password link
    try:
        uid = urlsafe_base64_decode(uidb64).decode() # decoding the user id
        user = Account._default_manager.get(pk=uid) # getting the user from the database
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid # storing the user id in the session
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
            uid = request.session.get('uid') # getting the user id from the session
            user = Account._default_manager.get(pk=uid) # getting the user from the database
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful. You can now log in with your new password.')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')
    
@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user = request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)


@login_required(login_url='login')
def edit_profile(request): # this function is for editing user profile
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user) #by passing this instance we can see the user details in the form
        profile_form = UserProfileForm(instance=userprofile) #by passing this instance we can see the user profile details in the form
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password) # check_password() is a built-in function in django that checks the password
            if success:
                user.set_password(new_password) #set_password() is a built-in function in django that sets the password
                user.save()
                # auth.logout(request) you can logout the user after changing the password or django will by default logout the user
                messages.success(request, 'Password changed successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Current password is incorrect.')
                return redirect('change_password')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')

@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product.price * i.quantity
    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'accounts/order_detail.html', context)
