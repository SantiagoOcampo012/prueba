from django.db import models

# Create your models here.
# ---------------------------------------------------------
#  METADATOS COMUNES
# ---------------------------------------------------------
class Metadatos(models.Model):
    creacion = models.DateTimeField("Fecha de Creación", auto_now_add=True)
    actualizacion = models.DateTimeField("Fecha de Actualización", auto_now=True)
    estado=models.BooleanField("Estado", default=True)
    
    class Meta:
        abstract = True
        
# ---------------------------------------------------------
#  ROL
# ---------------------------------------------------------
class Rol(Metadatos):
    nombre = models.CharField("Nombre", max_length=100, unique=True)
    descripcion = models.TextField("Descripción", blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "commons.rol"
        verbose_name = "Rol"
        verbose_name_plural = "Roles"


class Extension(Metadatos):
    nombre=models.CharField("Extencion", max_length=20)
    
    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "auth.extension"
        verbose_name = "Extension"
        verbose_name_plural = "Extensiones" 



def upload_to_app(instance, filename):
    # Obtener el nombre de la app desde el modelo
    app_label = instance._meta.app_label  
    return f"{app_label}/rutas/{filename}"

class File(Metadatos):
    extension = models.ForeignKey(Extension, on_delete=models.SET_NULL, null=True, blank=True)
    ruta = models.FileField(upload_to=upload_to_app)

    def __str__(self):
        return str(self.ruta)
    
    class Meta:
        db_table = "auth.ruta"
        verbose_name = "Ruta"
        verbose_name_plural = "Rutas" 

class Tipo(Metadatos):
    nombre=models.CharField("Nombre", max_length=100)
    tipo=models.CharField( max_length=100)

    def __str__(self):
        return str(self.nombre)
    
    class Meta:
        db_table = "auth.tipo"
        verbose_name = "Tipo"
        verbose_name_plural = "Tipos"
        
        
class Metodologias(Metadatos):
    nombre=models.CharField("Nombre", max_length=100)
    tipo = models.ForeignKey(Tipo, on_delete=models.SET_NULL, null=True, blank=True, related_name="metodologias")    
    def __str__(self):
        return str(self.nombre)
    
    class Meta:
        db_table = "auth.metodologia"
        verbose_name = "Metodologia"
        verbose_name_plural = "Metodologias"
        
        
class Estado(Metadatos):
    nombre=models.CharField("Nombre", max_length=100)
    tipo = models.ForeignKey(Tipo, on_delete=models.SET_NULL, null=True, blank=True, related_name="estados")    
    def __str__(self):
        return str(self.nombre)
    
    class Meta:
        db_table = "auth.estado"
        verbose_name = "Estado"
        verbose_name_plural = "Estados"
        
        
class Prioridad(Metadatos):
    nombre=models.CharField("Nombre", max_length=100)
    tipo = models.ForeignKey(Tipo, on_delete=models.SET_NULL, null=True, blank=True, related_name="prioridades")    
    def __str__(self):
        return str(self.nombre)
    
    class Meta:
        db_table = "auth.prioridad"
        verbose_name = "Prioridad"
        verbose_name_plural = "Prioridades"