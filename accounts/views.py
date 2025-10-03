from django.contrib import messages, auth
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from accounts.forms import RegistrationForm
from accounts.models import Account

#Verification by email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
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
            messages.success(request, 'Your account has been registered successfully!')
            return redirect('register')

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
            auth.login(request, user)
            #messages.success(request, 'You are now logged in.')
            return redirect('home')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')

def activate(request, uidb64, token):
    return HttpResponse('ok')
