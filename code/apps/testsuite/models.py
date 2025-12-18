from django.db import models
from apps.proyectos.models import Proyecto
from core import settings
from apps.commons.models import Metadatos


class TestSuite(Metadatos):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    proyecto = models.ForeignKey("proyectos.Proyecto", on_delete=models.PROTECT)

    def __str__(self):
        return self.nombre
    
    class Meta:
        db_table = "testsuite.testsuite"
        verbose_name = "Test Suite"
        verbose_name_plural = "Test Suites"


class Entorno(Metadatos):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre
    
    class Meta:
        db_table = "testsuite.entorno"
        verbose_name = "Entorno"
        verbose_name_plural = "Entornos"


class CasoPrueba(Metadatos):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    test_suite = models.ForeignKey(TestSuite, on_delete=models.SET_NULL, null=True, blank=True)
    estado = models.ForeignKey(
        'commons.Estado', on_delete=models.SET_NULL, null=True, blank=True, related_name="casoprueba_estado"
    )
    version = models.CharField(max_length=50)
    entorno = models.ForeignKey(Entorno, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        db_table = "testsuite.casoprueba"
        verbose_name = "Caso Prueba"
        verbose_name_plural = "Casos Pruebas"


class EjecucionPrueba(Metadatos):
    caso_prueba = models.ForeignKey(CasoPrueba, on_delete=models.SET_NULL, null=True, blank=True)
    ejecutado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    estado = models.ForeignKey(
        'commons.Estado', on_delete=models.SET_NULL, null=True, blank=True, related_name="ejecucionprueba_estado"
    )
    observaciones = models.TextField(blank=True)
    archivo = models.ForeignKey(
        'commons.File', on_delete=models.SET_NULL, null=True, blank=True
    )
    resultado = models.CharField(max_length=100)

    def __str__(self):
        return f"Ejecución de {self.caso_prueba.nombre if self.caso_prueba else 'N/A'} - {self.resultado}"

    class Meta:
        db_table = "testsuite.ejecucionprueba"
        verbose_name = "Ejecución Prueba"
        verbose_name_plural = "Ejecuciones Pruebas"
