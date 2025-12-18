import re
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.password_validation import validate_password
from apps.commons.models import Metadatos, Rol


# ---------------------------------------------------------
#  DOMINIO PERMITIDO
# ---------------------------------------------------------
class DominioPermitido(Metadatos):
    nombre = models.CharField("Dominio", max_length=255, unique=True)
    activo = models.BooleanField("Activo", default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "auth.dominio_permitido"
        verbose_name = "Dominio Permitido"
        verbose_name_plural = "Dominios Permitidos"


class Pais(Metadatos):
    nombre=models.CharField(max_length=200)
    prefijo=models.CharField(max_length=200)
    codigo_iso=models.CharField(max_length=200)
    
    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "auth.pais"
        verbose_name = "Pais"
        verbose_name_plural = "Paises"



class DivisionRegional(Metadatos):
    pais=models.ForeignKey(Pais, on_delete=models.PROTECT)
    nombre=models.CharField("Division regiona/ Departamento",max_length=200)
    
    
    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "auth.division_regional"
        verbose_name = "Division Regional"
        verbose_name_plural = "Divisiones Regionales / Departamentos"
        
class DivisionLocal(Metadatos):
    division_regional=models.ForeignKey(DivisionRegional, on_delete=models.PROTECT)
    nombre=models.CharField("Division local/ Municipio",max_length=200)
    
    
    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "auth.division_local"
        verbose_name = "Division Local"
        verbose_name_plural = "Divisiones Locales / Municipios"




# ---------------------------------------------------------
#  USUARIO MANAGER
# ---------------------------------------------------------
class UsuarioManager(BaseUserManager):
    """Manager personalizado para crear usuarios y superusuarios."""

    def create_user(self, correo, nick, password=None, **extra_fields):
        if not correo:
            raise ValueError("El correo es obligatorio.")
        if not nick:
            raise ValueError("El nickname es obligatorio.")

        correo = self.normalize_email(correo).lower()
        
        # Generar slug automático
        slug = slugify(nick)
        base_slug = slug
        contador = 1
        while self.model.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{contador}"
            contador += 1
        
        extra_fields.setdefault('slug', slug)
        user = self.model(correo=correo, nick=nick, **extra_fields)
        if password:
            validate_password(password, user)
            user.set_password(password)
        else:
            raise ValueError("La contraseña es obligatoria.")

        user.save(using=self._db)
        return user

    def create_superuser(self, correo, nick, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(correo, nick, password, **extra_fields)


# ---------------------------------------------------------
#  USUARIO PERSONALIZADO
# ---------------------------------------------------------
class Usuario(AbstractBaseUser, PermissionsMixin, Metadatos):
    nick = models.CharField("Nickname", max_length=100, unique=True)
    slug = models.SlugField("Slug", max_length=120, unique=True, blank=True)
    correo = models.EmailField("Correo electrónico", unique=True)
    idioma = models.CharField("Idioma", max_length=10, default="es")
    zona_horaria = models.CharField("Zona Horaria", max_length=50, default="UTC")

    # Bloqueo por intentos fallidos de contraseña
    intentos_fallidos = models.IntegerField(default=0)
    ultimo_intento = models.DateTimeField(null=True, blank=True)
    bloqueado_hasta = models.DateTimeField(null=True, blank=True)

    # Bloqueo MFA
    mfa_fallos_consecutivos = models.IntegerField(default=0)
    mfa_nivel_bloqueo = models.IntegerField(default=0)
    mfa_bloqueo_expiracion = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField("Habilitado", default=True)
    is_staff = models.BooleanField("Acceso al Admin", default=False)

    roles = models.ManyToManyField(Rol, related_name="usuarios", blank=True)

    objects = UsuarioManager()

    USERNAME_FIELD = "correo"
    REQUIRED_FIELDS = ["nick"]

    def esta_bloqueado(self) -> bool:
        """Verifica si el usuario está bloqueado por intentos fallidos de contraseña"""
        return bool(self.bloqueado_hasta and self.bloqueado_hasta > timezone.now())

    def esta_bloqueado_mfa(self) -> bool:
        """Verifica si el usuario está bloqueado por intentos fallidos de MFA"""
        return bool(self.mfa_bloqueo_expiracion and self.mfa_bloqueo_expiracion > timezone.now())

    def clean(self):
        # Correo válido
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", self.correo):
            raise ValidationError("El correo electrónico no es válido.")

        # Nickname válido
        if not re.match(r"^[a-zA-Z0-9_]+$", self.nick):
            raise ValidationError("El nickname solo puede contener letras, números y guiones bajos.")

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nick)
            slug = base_slug
            contador = 1
            while Usuario.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{contador}"
                contador += 1
            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.correo

    def crear_token_activacion(self):
        """Crea o devuelve un token de activación válido"""
        token_existente = self.tokens_activacion.filter(
            usado=False, 
            fecha_expiracion__gt=timezone.now()
        ).first()
        if token_existente:
            return token_existente
        return TokenActivacion.objects.create(usuario=self)

    class Meta:
        db_table = "auth.usuario"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"


# ---------------------------------------------------------
#  AUTENTICACIÓN MULTIFACTOR
# ---------------------------------------------------------
class AutenticacionMultifactor(Metadatos):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="codigos_mfa")
    codigo_verificacion = models.CharField(max_length=6)
    fecha_expiracion = models.DateTimeField()
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    usado = models.BooleanField(default=False) # <--- AÑADIDO: Para evitar que un código ya usado bloquee el reenvío (Bug 1)

    def expirado(self):
        return timezone.now() > self.fecha_expiracion
    
    def marcar_como_usado(self): # <--- AÑADIDO: Método para marcarlo como usado (Bug 1)
        self.usado = True
        self.save(update_fields=["usado"])

    def __str__(self):
        return f"MFA para {self.usuario.correo}"

    class Meta:
        db_table = "auth.mfa"
        verbose_name = "Autenticación Multifactor"
        verbose_name_plural = "Autenticaciones Multifactor"


# ---------------------------------------------------------
#  TOKEN DE ACTIVACIÓN DE CUENTA
# ---------------------------------------------------------
class TokenActivacion(Metadatos):
    usuario = models.ForeignKey("Usuario", on_delete=models.CASCADE, related_name="tokens_activacion")
    token = models.CharField(max_length=64, unique=True, editable=False)
    fecha_expiracion = models.DateTimeField()
    usado = models.BooleanField(default=False)

    DURACION_HORAS = 12

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = default_token_generator.make_token(self.usuario)
        if not self.fecha_expiracion:
            self.fecha_expiracion = timezone.now() + timedelta(hours=self.DURACION_HORAS)
        super().save(*args, **kwargs)

    def expirado(self):
        return timezone.now() > self.fecha_expiracion

    def marcar_como_usado(self):
        self.usado = True
        self.save(update_fields=["usado"])

    def __str__(self):
        return f"Token de {self.usuario.correo}"

    class Meta:
        db_table = "auth.token_activacion"
        verbose_name = "Token de Activación"
        verbose_name_plural = "Tokens de Activación"