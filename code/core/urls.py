from django.contrib import admin
from django.urls import path, include

from core import settings
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.autenticacion.urls')),
    path('bugtracker/', include('apps.bugtracker.urls')),
    path('historial/', include('apps.historial.urls')),
    path('notificaciones/', include('apps.notificaciones.urls')),
    path('proyectos/', include('apps.proyectos.urls')),
    path('reports/', include('apps.reports.urls')),
    path('testsuite/', include('apps.testsuite.urls')),
    path('tickets/', include('apps.tickets.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)