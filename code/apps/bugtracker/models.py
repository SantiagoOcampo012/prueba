from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

from apps.commons.models import Estado, Prioridad, File, Metadatos
from apps.proyectos.models import Proyecto
from apps.proyectos.models import Sprint

class Bug(Metadatos):

    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()

    severidad = models.ForeignKey(
        Prioridad,
        verbose_name="Severidad",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="severidad",
    )
    estado = models.ForeignKey(
        Estado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bug_estado",
    )

    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="proyecto",
    )
    sprint = models.ForeignKey(
        Sprint, on_delete=models.SET_NULL, null=True, blank=True, related_name="sprint"
    )

    reportado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bugs_reportados",
    )

    asignado_a = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bugs_asignados",
    )
    prioridad = models.ForeignKey(
        Prioridad,
        verbose_name="Prioridad",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prioridad",
    )
    archivo = models.ForeignKey(File, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.titulo

    class Meta:
        db_table = "auth.bug"
        verbose_name = "Bug"
        verbose_name_plural = "Bugs"


class ComentarioBug(Metadatos):
    bug = models.ForeignKey(Bug, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    comentario = models.TextField()
    archivo = models.ForeignKey(File, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Comentario en {self.bug}"

    class Meta:
        db_table = "auth.comentario_bug"
        verbose_name = "Comentario Bug"
        verbose_name_plural = "Comentarios Bugs"
