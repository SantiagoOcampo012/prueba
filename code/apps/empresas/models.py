from django.db import models
from apps.autenticacion.models import Metadatos, Usuario, DivisionLocal
from apps.proyectos.models import Proyecto


class Empresa(Metadatos):
    nit = models.CharField("Nit", max_length=200)
    nombre = models.CharField("Nombre", max_length=255)
    direccion = models.CharField("Direccion", max_length=200)
    telefono = models.CharField("Telefono", max_length=200)
    correo = models.CharField("Correo", max_length=200)

    usuario = models.ManyToManyField(
        Usuario, 
        through="Empresa_Usuario",
        related_name="empresas"
    )

    proyecto = models.ManyToManyField(
        Proyecto, 
        through="Empresa_Proyecto",
        related_name="empresas_proyectos"
    )

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "auth.empresa"
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"


class Empresa_Usuario(Metadatos):
    usuario = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name="empresa_usuario"
    )
    empresa = models.ForeignKey(
        Empresa, on_delete=models.SET_NULL, null=True, blank=True, related_name="empresa_usuario"
    )

    def __str__(self):
        return f"{self.usuario} - {self.empresa}"

    class Meta:
        db_table = "auth.empresa_usuario"
        verbose_name = "Empresa Usuario"
        verbose_name_plural = "Empresas Usuarios"
        unique_together = ("usuario", "empresa")


class Sucursal(Metadatos):
    empresa = models.ForeignKey(
        Empresa, on_delete=models.SET_NULL, null=True, blank=True, related_name="sucursales"
    )
    nombre = models.CharField("Nombre", max_length=255)
    ubicacion = models.ForeignKey(
        DivisionLocal, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.nombre} - {self.empresa}"

    class Meta:
        db_table = "auth.sucursal"
        verbose_name = "Sucursal"
        verbose_name_plural = "Sucursales"


class Empresa_Proyecto(Metadatos):
    empresa = models.ForeignKey(
        'empresas.Empresa', on_delete=models.SET_NULL, null=True, blank=True, related_name="empresa_proyectos"
    )
    proyecto = models.ForeignKey(
         'proyectos.Proyecto', on_delete=models.SET_NULL, null=True, blank=True, related_name="empresa_proyectos"
    )
    usuario = models.ForeignKey(
        'autenticacion.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name="empresa_proyectos"
    )

    def __str__(self):
        return f"{self.empresa} - {self.proyecto} ({self.usuario})"

    class Meta:
        db_table = "auth.empresa_proyecto"
        verbose_name = "Empresa Proyecto"
        verbose_name_plural = "Empresas Proyectos"
        unique_together = ("empresa", "proyecto", "usuario")
