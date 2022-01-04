from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=200)
    password1 = forms.CharField(widget=forms.PasswordInput())
    username = forms.CharField(help_text=False)
    
    class Meta:
        model = User
        fields = (
            'email',            
        	'username',
        )
