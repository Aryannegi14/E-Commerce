from django import forms
from django.contrib.auth.models import User
from .models import Review, Profile, Order
import re
from django.core.exceptions import ValidationError

   # Sign Up form
class SignUpForm(forms.ModelForm):
       password = forms.CharField(widget=forms.PasswordInput)

       class Meta:
           model = User
           fields = ['username', 'email', 'password']

   # Sign In form
class SignInForm(forms.Form):
       username = forms.CharField(max_length=100)
       password = forms.CharField(widget=forms.PasswordInput)

   # Review form for adding reviews
class ReviewForm(forms.ModelForm):
       class Meta:
           model = Review
           fields = ['text', 'rating', 'photo', 'video']

   # Username validation
def validate_username(value):
       if not re.match(r'^[\w]+$', value):
           raise ValidationError("Username should only contain letters, numbers, and underscores, with no spaces or special characters.")

   # User Registration form (redundant, can be removed since SignUpForm is used)
class UserRegistrationForm(forms.Form):
       username = forms.CharField(max_length=30, validators=[validate_username])
       email = forms.EmailField()
       password = forms.CharField(widget=forms.PasswordInput)

   # Profile update form
class ProfileForm(forms.ModelForm):
       class Meta:
           model = Profile
           fields = ['pfp']

   # Order form
class OrderForm(forms.ModelForm):
       class Meta:
           model = Order
           fields = [
               'name',
               'phone',
               'email',
               'address1',
               'address2',
               'city',
               'postal_code',
               'state',
           ]
           widgets = {
               'name': forms.TextInput(attrs={'class': 'form-input'}),
               'phone': forms.TextInput(attrs={'class': 'form-input'}),
               'email': forms.EmailInput(attrs={'class': 'form-input'}),
               'address1': forms.TextInput(attrs={'class': 'form-input'}),
               'address2': forms.TextInput(attrs={'class': 'form-input'}),
               'city': forms.TextInput(attrs={'class': 'form-input'}),
               'postal_code': forms.TextInput(attrs={'class': 'form-input'}),
               'state': forms.TextInput(attrs={'class': 'form-input'}),
           }