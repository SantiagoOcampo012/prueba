from django.urls import path
from . import views

app_name = 'testsuite'

urlpatterns = [
    # TestSuite URLs
    path('testsuites/', views.lista_testsuites, name='lista_testsuites'),
    path('testsuites/crear/', views.crear_testsuite, name='crear_testsuite'),
    path('testsuites/<int:pk>/editar/', views.editar_testsuite, name='editar_testsuite'),
    path('testsuites/<int:pk>/eliminar/', views.eliminar_testsuite, name='eliminar_testsuite'),
    path('testsuites/<int:pk>/detalle/', views.detalle_testsuite, name='detalle_testsuite'),
    
    # CasoPrueba URLs
    path('casos-prueba/', views.lista_casos_prueba, name='lista_casos'),
    path('casos-prueba/crear/', views.crear_caso_prueba, name='crear_caso_prueba'),
    path('casos-prueba/<int:pk>/editar/', views.editar_caso_prueba, name='editar_caso_prueba'),
    path('casos-prueba/<int:pk>/eliminar/', views.eliminar_caso_prueba, name='eliminar_caso_prueba'),
    path('casos-prueba/<int:pk>/detalle/', views.detalle_caso_prueba, name='detalle_caso_prueba'),
    
    # EjecucionPrueba URLs
    path('ejecuciones/', views.lista_ejecuciones, name='lista_ejecuciones'),
    path('ejecuciones/crear/', views.crear_ejecucion, name='crear_ejecucion'),
    path('ejecuciones/<int:pk>/editar/', views.editar_ejecucion, name='editar_ejecucion'),
    path('ejecuciones/<int:pk>/eliminar/', views.eliminar_ejecucion, name='eliminar_ejecucion'),
    path('ejecuciones/<int:pk>/detalle/', views.detalle_ejecucion, name='detalle_ejecucion'),


    # Entorno URLs
    path('entornos/', views.lista_entornos, name='lista_entornos'),
    path('entornos/crear/', views.crear_entorno, name='crear_entorno'),
    path('entornos/<int:pk>/editar/', views.editar_entorno, name='editar_entorno'),
    path('entornos/<int:pk>/eliminar/', views.eliminar_entorno, name='eliminar_entorno'),
    
    path('descargar-archivo/<int:pk>/', views.descargar_archivo, name='descargar_archivo'),

]
