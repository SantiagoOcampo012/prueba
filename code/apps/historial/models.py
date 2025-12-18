from django.db import models
from django.conf import settings

from apps.proyectos.models import Proyecto
from apps.tickets.models import Ticket, ComentarioTicket
from apps.bugtracker.models import Bug, ComentarioBug
from apps.autenticacion.models import Usuario
from apps.commons.models import Estado, Metadatos
from apps.testsuite.models import EjecucionPrueba,TestSuite
from apps.reports.models import Reporte

class Historial(Metadatos):
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True,blank=True)
    estado=models.ForeignKey(Estado, on_delete=models.SET_NULL,null=True,blank=True)
    descripcion = models.TextField(blank=True)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.SET_NULL, null=True, blank=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.SET_NULL, null=True, blank=True)
    bug = models.ForeignKey(Bug, on_delete=models.SET_NULL, null=True, blank=True)
    ejecucion_prueba=models.ForeignKey(EjecucionPrueba, on_delete=models.SET_NULL, null=True, blank=True)
    testsuite=models.ForeignKey(TestSuite, on_delete=models.SET_NULL, null=True, blank=True)
    reportes=models.ForeignKey(Reporte, on_delete=models.SET_NULL, null=True, blank=True)
    comentario_bug=models.ForeignKey(ComentarioBug, on_delete=models.SET_NULL, null=True, blank=True)
    comentario_ticket=models.ForeignKey(ComentarioTicket, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.usuario.nick}"
    class Meta:
        db_table = "auth.historial"
        verbose_name = "Historial"
        verbose_name_plural = "Historiales"

class DetalleHistorial(Metadatos):
    historial = models.ForeignKey(Historial, on_delete=models.PROTECT, related_name="detalles")
    campo = models.CharField(max_length=100)
    valor_anterior = models.TextField(null=True, blank=True)
    valor_nuevo = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Detalle {self.campo} en {self.historial.id}"

    class Meta:
        db_table = "auth.detallehistorial"
        verbose_name = "Detalle Historial"
        verbose_name_plural = "Detalles Historiales"
