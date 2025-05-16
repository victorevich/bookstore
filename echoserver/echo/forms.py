from django import forms
from .models import Books, User, Order
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
class BookForm(forms.ModelForm):
    class Meta:
        model = Books
        fields = ['title', 'author', 'price']


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=150,
        label='Имя пользователя',
        help_text='Введите ваше имя пользователя'
    )
    class Meta:
        model = User
        fields = ['username', 'password']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'

class UserProfileForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password != password_confirm:
            raise forms.ValidationError("Пароли не совпадают")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)  # Хэширует пароль
        if commit:
            user.save()
        return user