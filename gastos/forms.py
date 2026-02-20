from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import re
from django.core.exceptions import ValidationError
from .models import Gasto


class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput,
        help_text="Sua senha deve ter 8 caracteres, 1 letra maiúscula e 1 caractere especial"
    )

    def clean_password1(self):
        password = self.cleaned_data.get('password1')

        if len(password) < 8:
            raise ValidationError("Sua senha deve ter no mínimo 8 caracteres.")

        if not re.search(r'[A-Z]', password):
            raise ValidationError("Sua senha deve conter pelo menos 1 letra maiúscula.")

        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
            raise ValidationError("Sua senha deve conter pelo menos 1 caractere especial.")

        return password


class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ['data', 'categoria', 'descricao', 'valor']

        labels = {
            'data': 'Data',
            'categoria': 'Categoria',
            'descricao': 'Descrição',
            'valor': 'Valor',
        }

        widgets = {
            'data': forms.DateInput(attrs={
                'type': 'date',
                'class': 'input-field'
            }),
            'categoria': forms.TextInput(attrs={
                'placeholder': 'Ex: Alimentação',
                'class': 'input-field'
            }),
            'descricao': forms.TextInput(attrs={
                'placeholder': 'Ex: Mercado do mês',
                'class': 'input-field'
            }),
            'valor': forms.NumberInput(attrs={
                'placeholder': 'Ex: 150.00',
                'step': '0.01',
                'class': 'input-field'
            }),
        }
