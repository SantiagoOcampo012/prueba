from django.db import models
from django.conf import settings
from apps.autenticacion.models import Usuario
from apps.bugtracker.models import Bug, ComentarioBug
from apps.commons.models import Tipo,Metadatos
from apps.proyectos.models import Proyecto
from apps.reports.models import Reporte
from apps.testsuite.models import EjecucionPrueba, TestSuite
from apps.tickets.models import ComentarioTicket, Ticket

class Notificacion(Metadatos):

    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    titulo = models.CharField(max_length=150)
    mensaje = models.TextField()
    tipo = models.ForeignKey(Tipo, on_delete=models.SET_NULL, null=True,blank=True)
    leida = models.BooleanField(default=False)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.SET_NULL, null=True, blank=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.SET_NULL, null=True, blank=True)
    bug = models.ForeignKey(Bug, on_delete=models.SET_NULL, null=True, blank=True)
    ejecucion_prueba=models.ForeignKey(EjecucionPrueba, on_delete=models.SET_NULL, null=True, blank=True)
    testsuite=models.ForeignKey(TestSuite, on_delete=models.SET_NULL, null=True, blank=True)
    reportes=models.ForeignKey(Reporte, on_delete=models.SET_NULL, null=True, blank=True)
    comentario_bug=models.ForeignKey(ComentarioBug, on_delete=models.SET_NULL, null=True, blank=True)
    comentario_ticket=models.ForeignKey(ComentarioTicket, on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self):
        return f"{self.titulo} → {self.usuario.nick}"


    class Meta:
        db_table = "auth.notificacion"
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"


class ConfiguracionNotificacion(Metadatos):
    usuario = models.OneToOneField(Usuario, on_delete=models.PROTECT)
    recibir_correos = models.BooleanField(default=True)
    recibir_alertas_app = models.BooleanField(default=True)

    def __str__(self):
        return f"Configuración de {self.usuario.nick}"
    
    class Meta:
        db_table = "auth.configuracion_notificacion"
        verbose_name = "Configuración de Notificación"
        verbose_name_plural = "Configuraciones de Notificaciones"