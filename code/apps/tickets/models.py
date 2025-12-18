from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from apps.commons.models import Metadatos

class Ticket(Metadatos):
    ESTADOS = [
        ('ABIERTO', 'Abierto'),
        ('EN_PROGRESO', 'En progreso'),
        ('RESUELTO', 'Resuelto'),
        ('CERRADO', 'Cerrado'),
    ]

    PRIORIDADES = [
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
        ('CRITICA', 'Crítica'),
    ]

    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()

    proyecto = models.ForeignKey('proyectos.Proyecto', on_delete=models.SET_NULL, null=True, blank=True )
    sprint = models.ForeignKey('proyectos.Sprint', on_delete=models.SET_NULL, null=True, blank=True)

    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets_creados')
    asignado_a = models.ForeignKey("empresas.Empresa_Proyecto", on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets_asignados')

    estado = models.ForeignKey('commons.Estado', on_delete=models.SET_NULL, null=True, blank=True, related_name="ticket_estado")
    prioridad = models.ForeignKey('commons.Prioridad', on_delete=models.SET_NULL, null=True, blank=True, related_name="ticket_prioridad")
    archivo=models.ForeignKey(
        'commons.File', on_delete=models.SET_NULL, null=True, blank=True)

    tipo_ticket=models.ForeignKey('commons.Tipo', on_delete=models.SET_NULL, null=True, blank=True, related_name="ticket_tipo_ticket")

    def __str__(self):
        return self.titulo

    class Meta:
        db_table = "tickets.ticket"
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"

class ComentarioTicket(Metadatos):
    ticket = models.ForeignKey(Ticket, on_delete=models.SET_NULL, null=True, blank=True)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    contenido = models.TextField()
    archivo=models.ForeignKey(
        'commons.File', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Comentario en {self.ticket}"

    class Meta:
        db_table = "tickets.comentarioticket"
        verbose_name = "Comentario Ticket"
        verbose_name_plural = "Comentarios Tickets"
        

class HistorialTicket(Metadatos):
    ticket = models.ForeignKey(Ticket, on_delete=models.PROTECT)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    estado = models.ForeignKey('commons.Estado', on_delete=models.SET_NULL, null=True, blank=True)
    descripcion = models.TextField(blank=True, null=True)
    

    def __str__(self):
        return f"Historial de {self.ticket}"

    class Meta:
        db_table = "tickets.historialticket"
        verbose_name = "Historial Ticket"
        verbose_name_plural = "Historiales Tickets"