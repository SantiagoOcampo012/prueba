from django.db import models
from django.conf import settings

from apps.proyectos.models import Proyecto
from apps.testsuite.models import TestSuite
from apps.commons.models import Metadatos,Tipo,Estado,File

# Create your models here.
class Reporte(Metadatos):

    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    tipo = models.ForeignKey(Tipo, on_delete=models.SET_NULL, null=True, blank=True)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.SET_NULL, null=True, blank=True)
    testsuite = models.ForeignKey(TestSuite, on_delete=models.SET_NULL, null=True, blank=True)
    generado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    estado = models.ForeignKey(Estado, on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self):
        return self.titulo
    
    class Meta:
        db_table = "reports.reporte"
        verbose_name = "Reporte"
        verbose_name_plural = "Reportes"
    
class ArchivoReporte(Metadatos):
    reporte = models.ForeignKey(Reporte, on_delete=models.CASCADE)
    archivo = models.ForeignKey(File, on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self):
        return f"Archivo de {self.reporte.titulo}"

    class Meta:
        db_table = "reports.archivoreporte"
        verbose_name = "Archivo Reporte"
        verbose_name_plural = "Archivos Reportes"