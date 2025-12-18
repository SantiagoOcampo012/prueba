from django.urls import path
from . import views

app_name = "proyectos" 

urlpatterns = [
    path('', views.lista_proyectos, name='lista_proyectos'),
    path('crear/', views.crear_proyecto, name='crear_proyecto'),
    path('<int:id>/', views.detalle_proyecto, name='detalle_proyecto'),
    path('<int:proyecto_id>/agregar-miembro/', views.agregar_miembro, name='agregar_miembro'),
    path('<int:proyecto_id>/crear-sprint/', views.crear_sprint, name='crear_sprint'),
    path('<int:proyecto_id>/crear-tarea/', views.crear_tarea, name='crear_tarea'),
    path('<int:proyecto_id>/agregar-metodologia/', views.agregar_metodologia, name='agregar_metodologia'),
]