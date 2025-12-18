# apps/email/managers.py

from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError


class UsuarioManager(BaseUserManager):
    """Manager personalizado para el modelo Usuario."""

    def create_user(self, correo, password=None, **extra_fields):
        """Crea y guarda un usuario con correo y contraseña."""
        if not correo:
            raise ValueError("El campo 'correo' es obligatorio.")

        correo = self.normalize_email(correo)
        user = self.model(correo=correo, **extra_fields)

        # ✅ Establecer contraseña antes de validar
        user.set_password(password or None)

        try:
            user.full_clean()  # Validaciones del modelo
            user.save(using=self._db)
        except ValidationError as e:
            raise ValueError(e.message_dict) from e

        return user

    def create_superuser(self, correo, password=None, **extra_fields):
        """Crea y guarda un superusuario."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("El superusuario debe tener is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("El superusuario debe tener is_superuser=True.")

        return self.create_user(correo, password, **extra_fields)
