from django.contrib import admin
from .models import Proyecto, MiembroProyecto, ProyectoMetodologia, Sprint

# Register your models here.
admin.site.register(Proyecto)
admin.site.register(MiembroProyecto)
admin.site.register(ProyectoMetodologia)
admin.site.register(Sprint)