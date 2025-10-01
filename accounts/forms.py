from django import forms
from .models import Account

class RegistrationForm(forms.ModelForm): # this is for registration form
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'}))
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email','phone_number', 'password']

    def __init__(self, *args, **kwargs):# this gives form-control class to all the fields and placeholder to the fields
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter first name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter last name'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter email'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter phone number'
        for filed in self.fields:
            self.fields[filed].widget.attrs['class'] = 'form-control' # this gives form-control class (css) to all the fields
    

    def clean(self):# this is for password matching
        cleaned_data = super(RegistrationForm, self).clean() 
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Password doesn't match")
