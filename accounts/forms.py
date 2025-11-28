from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, EmployeeGroup


class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'phone', 'password1', 'password2')


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'phone', 'avatar')


class EmployeeGroupForm(forms.ModelForm):
    class Meta:
        model = EmployeeGroup
        fields = ('name', 'description', 'moderators')
        widgets = {
            'moderators': forms.CheckboxSelectMultiple,
        }

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label='Имя пользователя',
        widget=forms.TextInput(attrs={'name': 'username'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'name': 'password'})
    )
