from django.urls import path
from . import views

app_name = 'bugtracker'

urlpatterns = [
    # Lista y CRUD de bugs
    path('bugs/', views.lista_bugs, name='lista_bugs'),
    path('bugs/crear/', views.crear_bug, name='crear_bug'),
    path('bugs/<int:bug_id>/', views.detalle_bug, name='detalle_bug'),
    path('bugs/<int:bug_id>/editar/', views.editar_bug, name='editar_bug'),
    path('bugs/<int:bug_id>/eliminar/', views.eliminar_bug, name='eliminar_bug'),
    path('bugs/<int:bug_id>/solicitar-revision/', views.solicitar_revision, name='solicitar_revision'),
    
    # Comentarios
    path('bugs/<int:bug_id>/comentarios/agregar/', views.agregar_comentario, name='agregar_comentario'),
    path('comentarios/<int:comentario_id>/editar/', views.editar_comentario, name='editar_comentario'),
    path('comentarios/<int:comentario_id>/eliminar/', views.eliminar_comentario, name='eliminar_comentario'),
]