# apps/autenticacion/admin.py
from django.contrib import admin
from .models import Rol, Extension, File, Tipo, Metodologias, Estado, Prioridad

# ----------------------------
# Admin Roles
# ----------------------------
@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion", "estado", "creacion", "actualizacion")
    list_filter = ("estado",)
    search_fields = ("nombre", "descripcion")
    readonly_fields = ("creacion", "actualizacion")
    ordering = ("nombre",)

# ----------------------------
# Admin Extension
# ----------------------------
@admin.register(Extension)
class ExtensionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "estado", "creacion", "actualizacion")
    list_filter = ("estado",)
    search_fields = ("nombre",)
    readonly_fields = ("creacion", "actualizacion")
    ordering = ("nombre",)

# ----------------------------
# Admin File
# ----------------------------
@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("ruta", "extension", "estado", "creacion", "actualizacion")
    list_filter = ("estado", "extension")
    search_fields = ("ruta",)
    readonly_fields = ("creacion", "actualizacion")
    ordering = ("ruta",)

# ----------------------------
# Admin Tipo
# ----------------------------
@admin.register(Tipo)
class TipoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "estado", "creacion", "actualizacion")
    list_filter = ("estado", "tipo")
    search_fields = ("nombre", "tipo")
    readonly_fields = ("creacion", "actualizacion")
    ordering = ("nombre",)

# ----------------------------
# Admin Metodologias
# ----------------------------
@admin.register(Metodologias)
class MetodologiasAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "estado", "creacion", "actualizacion")
    list_filter = ("tipo", "estado")
    search_fields = ("nombre",)
    readonly_fields = ("creacion", "actualizacion")
    ordering = ("nombre",)

# ----------------------------
# Admin Estado
# ----------------------------
@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "estado", "creacion", "actualizacion")
    list_filter = ("tipo", "estado")
    search_fields = ("nombre",)
    readonly_fields = ("creacion", "actualizacion")
    ordering = ("nombre",)

# ----------------------------
# Admin Prioridad
# ----------------------------
@admin.register(Prioridad)
class PrioridadAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "estado", "creacion", "actualizacion")
    list_filter = ("tipo", "estado")
    search_fields = ("nombre",)
    readonly_fields = ("creacion", "actualizacion")
    ordering = ("nombre",)
