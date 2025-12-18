from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from apps.commons.models import Estado, Metadatos, Metodologias,Rol

class Proyecto(Metadatos):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.ForeignKey(Estado, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "proyectos.proyecto"
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"

class MiembroProyecto(Metadatos):
 
    proyecto = models.ForeignKey('empresas.Empresa_Proyecto', on_delete=models.SET_NULL, null=True, blank=True)
    rol = models.ForeignKey('commons.Rol', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.proyecto.usuario} en {self.proyecto} ({self.rol})"
    class Meta:
        db_table = "proyectos.miembroproyecto"
        verbose_name = "Miembro Proyecto"
        verbose_name_plural = "Miembros Proyectos"

class ProyectoMetodologia(Metadatos):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.SET_NULL,null=True,blank=True)
    metodologia = models.ForeignKey(Metodologias, on_delete=models.SET_NULL,null=True,blank=True)

    def __str__(self):
        return f"{self.metodologia} en {self.proyecto}"
    class Meta:
        db_table = "proyectos.proyectometodologia"
        verbose_name = "Proyecto Metodologia"
        verbose_name_plural = "Proyectos Metodologias"
        

class Sprint(Metadatos):

    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.ForeignKey(Estado, on_delete=models.SET_NULL, null=True, blank=True)

    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.nombre}"

    class Meta:
            db_table = "sprints.sprint"
            verbose_name = "Sprint"
            verbose_name_plural = "Sprints"
            
class Tarea(Metadatos):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    estado = models.ForeignKey(Estado, on_delete=models.SET_NULL, null=True, blank=True)
    prioridad = models.ForeignKey('commons.Prioridad', on_delete=models.SET_NULL, null=True, blank=True)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.SET_NULL, null=True, blank=True)
    sprint = models.ForeignKey(Sprint, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre}"

    class Meta:
            db_table = "sprints.tarea"
            verbose_name = "Tarea"
            verbose_name_plural = "Tareas"