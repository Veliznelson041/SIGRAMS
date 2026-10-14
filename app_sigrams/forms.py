import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from app_registros.validators import PasswordValidator

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': '[A-Za-záéíóúÁÉÍÓÚñÑ\\s]+',
            'title': 'Solo letras y espacios',
            'placeholder': 'Nombre'
        })
    )
    
    last_name = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': '[A-Za-záéíóúÁÉÍÓÚñÑ\\s]+',
            'title': 'Solo letras y espacios',
            'placeholder': 'Apellido'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'title': 'Ejemplo: usuario@dominio.com',
            'placeholder': 'usuario@ejemplo.com'
        })
    )
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': '[A-Za-z0-9_]+',
            'title': 'Letras, números y guiones bajos',
            'placeholder': 'Nombre de usuario'
        })
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'title': 'Mínimo 8 caracteres, una mayúscula, una minúscula, un número y un carácter especial',
            'placeholder': 'Contraseña'
        }),
        help_text='''<ul class="small">
            <li>Mínimo 8 caracteres</li>
            <li>Al menos una letra mayúscula</li>
            <li>Al menos una letra minúscula</li>
            <li>Al menos un número</li>
            <li>Al menos un carácter especial (!@#$%^&*)</li>
        </ul>'''
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar mensajes de error
        self.fields['username'].error_messages = {
            'unique': 'Este nombre de usuario ya existe.',
            'required': 'El nombre de usuario es obligatorio.'
        }
        self.fields['email'].error_messages = {
            'unique': 'Este email ya está registrado.',
            'required': 'El email es obligatorio.'
        }
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            if not re.match(r'^[A-Za-záéíóúÁÉÍÓÚñÑ\s]+$', first_name):
                raise forms.ValidationError(
                    'El nombre solo puede contener letras y espacios.',
                    code='invalid_first_name'
                )
            return first_name.title()
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            if not re.match(r'^[A-Za-záéíóúÁÉÍÓÚñÑ\s]+$', last_name):
                raise forms.ValidationError(
                    'El apellido solo puede contener letras y espacios.',
                    code='invalid_last_name'
                )
            return last_name.title()
        return last_name
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError(
                    'Este email ya está registrado. Por favor, use otro.',
                    code='duplicate_email'
                )
        return email
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            # Validar contraseña fuerte
            validator = PasswordValidator()
            try:
                validator(password1)
            except forms.ValidationError as e:
                raise forms.ValidationError(e.message)
        return password1