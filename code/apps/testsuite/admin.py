from django.contrib import admin
from .models import TestSuite, Entorno, CasoPrueba, EjecucionPrueba

# Register your models here.
admin.site.register(TestSuite)
admin.site.register(Entorno)
admin.site.register(CasoPrueba)
admin.site.register(EjecucionPrueba)