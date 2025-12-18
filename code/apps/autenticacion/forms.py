from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Usuario, AutenticacionMultifactor, TokenActivacion


# ---------------------------------------------------------
#  FORMULARIO DE REGISTRO
# ---------------------------------------------------------
class RegistroForm(forms.ModelForm):
    """Formulario para el registro de nuevos usuarios."""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}),
        label='Contraseña'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar Contraseña'}),
        label='Confirmar Contraseña'
    )

    class Meta:
        model = Usuario
        fields = ('nick', 'correo', 'password')
        widgets = {
            'nick': forms.TextInput(attrs={'placeholder': 'Tu Nickname Único'}),
            'correo': forms.EmailInput(attrs={'placeholder': 'Correo Electrónico'}),
        }
        labels = {
            'nick': 'Nickname',
            'correo': 'Correo Electrónico',
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            try:
                # Usa el validador de contraseña de Django
                validate_password(password, self.instance)
            except ValidationError as e:
                # Relanza el error para que Django lo muestre en el formulario
                self.add_error('password', e)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        
        return cleaned_data

    def save(self, commit=True):
        # Crear usuario con is_active=False por defecto (para activación por email)
        user = Usuario.objects.create_user(
            correo=self.cleaned_data['correo'],
            nick=self.cleaned_data['nick'],
            password=self.cleaned_data['password'],
            is_active=False, # Por defecto inactivo hasta que se active por correo
        )
        return user


# ---------------------------------------------------------
#  FORMULARIO DE LOGIN (Paso 1: Credenciales)
# ---------------------------------------------------------
class LoginForm(forms.Form):
    """Formulario para ingresar credenciales de usuario."""
    correo = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Correo Electrónico'}),
        label='Correo Electrónico'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}),
        label='Contraseña'
    )


# ---------------------------------------------------------
#  FORMULARIO DE MFA (Paso 2: Código)
# ---------------------------------------------------------
class MFAForm(forms.Form):
    """Formulario para ingresar el código de Autenticación Multifactor."""
    codigo = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={'placeholder': 'Código de 6 dígitos'}),
        label='Código de Verificación MFA'
    )


# ---------------------------------------------------------
#  FORMULARIO DE SOLICITUD DE ACTIVACIÓN
# ---------------------------------------------------------
class SolicitudActivacionForm(forms.Form):
    """Formulario para solicitar un nuevo enlace de activación de cuenta."""
    correo = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Correo Electrónico'}),
        label='Correo Electrónico'
    )


# ---------------------------------------------------------
#  FORMULARIO DE RECUPERACIÓN DE CONTRASEÑA (Solicitud)
# ---------------------------------------------------------
class RecuperacionPasswordForm(forms.Form):
    """Formulario para solicitar el enlace de recuperación de contraseña."""
    correo = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Correo Electrónico'}),
        label='Correo Electrónico'
    )


# ---------------------------------------------------------
#  FORMULARIO DE RESTABLECIMIENTO DE CONTRASEÑA (Cambio)
# ---------------------------------------------------------
class RestablecerPasswordForm(forms.Form):
    """Formulario para ingresar la nueva contraseña."""
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Nueva Contraseña'}),
        label='Nueva Contraseña'
    )
    new_password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar Nueva Contraseña'}),
        label='Confirmar Contraseña'
    )

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            try:
                # Usa el validador de contraseña de Django
                validate_password(new_password)
            except ValidationError as e:
                self.add_error('new_password', e)
        return new_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        new_password_confirm = cleaned_data.get("new_password_confirm")

        if new_password and new_password_confirm and new_password != new_password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        
        return cleaned_data