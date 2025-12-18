from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.utils import timezone

from .models import (
    Usuario,
    DominioPermitido,
    AutenticacionMultifactor,
    TokenActivacion
)


# Asumiendo que este formulario existe
# from .forms import UsuarioChangeForm


# --------------------------------------------------------------------------
# 1️⃣ DominioPermitido (editable normalmente)
# --------------------------------------------------------------------------

@admin.register(DominioPermitido)
class DominioPermitidoAdmin(admin.ModelAdmin):
    """Administración de los dominios de correo permitidos para el registro."""
    list_display = ("nombre", "activo", "creacion", "actualizacion")
    list_filter = ("activo",)
    search_fields = ("nombre",)
    ordering = ("nombre",)
    readonly_fields = ("creacion", "actualizacion")


# --------------------------------------------------------------------------
# 2️⃣ Rol (nuevo modelo)
# --------------------------------------------------------------------------



# --------------------------------------------------------------------------
# 🔒 Filtros Personalizados para Bloqueos de Seguridad 🔒
# --------------------------------------------------------------------------

class BloqueoCredencialesFilter(SimpleListFilter):
    title = _('Bloqueo Credenciales')
    parameter_name = 'bloqueado_credenciales'

    def lookups(self, request, model_admin):
        """Define las opciones del filtro: Sí (Bloqueado) o No (Activo)."""
        return [
            ('1', _('Sí')),
            ('0', _('No')),
        ]

    def queryset(self, request, queryset):
        """Filtra los usuarios basándose en la fecha de expiración del bloqueo de credenciales."""
        now = timezone.now()

        # Bloqueado: si la fecha de bloqueo es mayor a la hora actual
        if self.value() == '1':
            return queryset.filter(bloqueado_hasta__gt=now)

        # No Bloqueado: si la fecha es nula O si la fecha ya expiró
        if self.value() == '0':
            return queryset.filter(
                Q(bloqueado_hasta__isnull=True) | Q(bloqueado_hasta__lte=now)
            )

        return queryset


class BloqueoMFAFilter(SimpleListFilter):
    title = _('Bloqueo MFA')
    parameter_name = 'bloqueado_mfa'

    def lookups(self, request, model_admin):
        """Define las opciones del filtro: Sí (Bloqueado) o No (Activo)."""
        return [
            ('1', _('Sí')),
            ('0', _('No')),
        ]

    def queryset(self, request, queryset):
        """Filtra los usuarios basándose en la fecha de expiración del bloqueo MFA."""
        now = timezone.now()

        # Bloqueado: si la fecha de bloqueo MFA es mayor a la hora actual
        if self.value() == '1':
            return queryset.filter(mfa_bloqueo_expiracion__gt=now)

        # No Bloqueado: si la fecha es nula O si la fecha ya expiró
        if self.value() == '0':
            return queryset.filter(
                Q(mfa_bloqueo_expiracion__isnull=True) | Q(mfa_bloqueo_expiracion__lte=now)
            )

        return queryset


# --------------------------------------------------------------------------
# 3️⃣ Usuario (editable mínimo)
# --------------------------------------------------------------------------

@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """
    Panel de administración para Usuario.
    Permite ver/editar estado, contraseña y roles, incluyendo seguridad MFA.
    """
    # form = UsuarioChangeForm # Asumiendo que este formulario existe

    # 🔄 REORDENADO para poner la seguridad al frente
    list_display = (
        "correo",
        "nick",
        "bloqueo_credenciales_status",  # Muestra el estado de bloqueo por contraseña (Contraseña)
        "bloqueo_mfa_status",  # Muestra el estado de bloqueo por MFA (MFA)
        "expiracion_bloqueo_credenciales",  # Fecha de expiración del bloqueo de credenciales
        "mfa_bloqueo_expiracion",  # Fecha de expiración del bloqueo MFA
        "roles_list",
        "is_active",
        "is_staff",
        "creacion",
        "actualizacion",
        "estado"
    )

    # ⚙️ ACTUALIZADO: Usamos las clases de filtro personalizadas
    list_filter = (
        BloqueoCredencialesFilter,  # <-- Filtro personalizado
        BloqueoMFAFilter,  # <-- Filtro personalizado
        "is_active",
        "is_staff",
        "is_superuser",
        "roles"
    )
    search_fields = ("correo", "nick", "slug")
    ordering = ("correo",)

    fieldsets = (
        (None, {"fields": ("correo", "password")}),
        ("Estado de la Cuenta", {"fields": ("is_active",)}),
        ("Información Básica", {"fields": ("nick", "slug", "idioma", "zona_horaria")}),
        ("Seguridad General", {
            "fields": (
                "is_staff", "is_superuser", "roles",
                "groups", "user_permissions"
            )
        }),
        ("Bloqueo de Contraseña", {
            # Estos campos son solo de auditoría/visualización
            "fields": (
                "intentos_fallidos", "ultimo_intento", "bloqueado_hasta",
            ),
            "classes": ("collapse",)
        }),
        ("Bloqueo MFA (Multifactor)", {
            # Estos campos son solo de auditoría/visualización
            "fields": (
                "mfa_fallos_consecutivos",
                "mfa_nivel_bloqueo",
                "mfa_bloqueo_expiracion",
            ),
            "classes": ("collapse",)
        }),
        ("Metadatos", {"fields": ("creacion", "actualizacion")}),
    )

    # Todos los campos de seguridad son de solo lectura para evitar manipulación manual
    readonly_fields = (
        "nick", "slug", "idioma", "zona_horaria",
        "intentos_fallidos", "ultimo_intento", "bloqueado_hasta",
        # bloqueado_hasta se mantiene aquí para la vista del formulario
        "mfa_fallos_consecutivos", "mfa_nivel_bloqueo", "mfa_bloqueo_expiracion",
        "creacion", "actualizacion",
    )

    filter_horizontal = ("roles", "groups", "user_permissions")

    # --- Métodos de Listado ---

    # Mostrar roles en la lista
    def roles_list(self, obj):
        return ", ".join([r.nombre for r in obj.roles.all()])

    roles_list.short_description = "Roles"

    # Método que muestra el estado de bloqueo por credenciales (Contraseña)
    def bloqueo_credenciales_status(self, obj):
        """Muestra el estado de bloqueo por fallos de credenciales."""
        return obj.esta_bloqueado()

    bloqueo_credenciales_status.boolean = True
    bloqueo_credenciales_status.short_description = "Bloqueo Credenciales"

    # Método para renombrar bloqueado_hasta en la lista
    def expiracion_bloqueo_credenciales(self, obj):
        """Devuelve la fecha de expiración del bloqueo de credenciales."""
        return obj.bloqueado_hasta

    expiracion_bloqueo_credenciales.short_description = "Expiración Bloqueo Credenciales"

    # Método que muestra el estado de bloqueo por MFA
    def bloqueo_mfa_status(self, obj):
        """Muestra el estado de bloqueo MFA en la lista."""
        return obj.esta_bloqueado_mfa()

    bloqueo_mfa_status.boolean = True
    bloqueo_mfa_status.short_description = "Bloqueo MFA"

    # 🔒 Restricciones (se mantienen)
    def has_add_permission(self, request): return False

    def has_delete_permission(self, request, obj=None): return False

    def has_change_permission(self, request, obj=None): return True

    def has_view_permission(self, request, obj=None): return True


# --------------------------------------------------------------------------
# 4️⃣ AutenticacionMultifactor (solo lectura)
# --------------------------------------------------------------------------

@admin.register(AutenticacionMultifactor)
class AutenticacionMultifactorAdmin(admin.ModelAdmin):
    """Administración de códigos MFA (solo lectura)."""
    list_display = ("usuario", "codigo_verificacion", "fecha_expiracion", "expirado", "creacion")
    list_filter = ("fecha_expiracion",)
    search_fields = ("usuario__correo", "usuario__nick", "ip")
    readonly_fields = ("usuario", "codigo_verificacion", "fecha_expiracion", "ip", "user_agent", "creacion",
                       "actualizacion")

    def expirado(self, obj):
        return obj.expirado()

    expirado.boolean = True

    def has_add_permission(self, request): return False

    def has_change_permission(self, request, obj=None): return False

    def has_delete_permission(self, request, obj=None): return False


# --------------------------------------------------------------------------
# 5️⃣ TokenActivacion (solo lectura)
# --------------------------------------------------------------------------

@admin.register(TokenActivacion)
class TokenActivacionAdmin(admin.ModelAdmin):
    """Auditoría de tokens de activación de cuenta (solo lectura)."""
    list_display = (
        "usuario", "token_truncado", "creacion", "fecha_expiracion", "usado", "expirado_status"
    )
    list_filter = ("usado", "fecha_expiracion")
    search_fields = ("usuario__correo", "token")
    readonly_fields = ("usuario", "token", "creacion", "fecha_expiracion",
                       "actualizacion")

    def expirado_status(self, obj):
        return obj.expirado()

    expirado_status.boolean = True
    expirado_status.short_description = "Expirado"

    def token_truncado(self, obj):
        return f"{obj.token[:10]}..." if obj.token else ""

    token_truncado.short_description = "Token (Truncado)"

    def has_add_permission(self, request): return False

    def has_change_permission(self, request, obj=None): return False

    def has_delete_permission(self, request, obj=None): return False
