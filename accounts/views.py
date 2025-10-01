from django.shortcuts import redirect, render

from accounts.forms import RegistrationForm
from accounts.models import Account

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
           # return redirect('login')

    else: 
        form = RegistrationForm() 
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context )    

def login(request):
    return render(request, 'accounts/login.html')

def logout(request):
    return render