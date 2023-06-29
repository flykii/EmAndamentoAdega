
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class BaseUserForm(forms.ModelForm):
    password1 = forms.CharField(label='Senha', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label='Confirmar senha', widget=forms.PasswordInput, required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'user_type')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('As senhas não coincidem')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['password1']:
            user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class CustomUserCreationForm(BaseUserForm, UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Usuário'
        self.fields['email'].label = 'Email'

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        user_type = cleaned_data.get('user_type')

        if not username:
            self.add_error('username', 'O campo "Usuário" é obrigatório.')
        if not email:
            self.add_error('email', 'O campo "Email" é obrigatório.')
        if not user_type:
            self.add_error('user_type', 'O campo "Perfil de usuário" é obrigatório.')

        return cleaned_data

class CustomUserEditForm(BaseUserForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Usuário'
        self.fields['email'].label = 'Email'
