from django import forms
from .models import Books, User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
class BookForm(forms.ModelForm):
    class Meta:
        model = Books
        fields = ['title', 'author', 'price']
class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']
