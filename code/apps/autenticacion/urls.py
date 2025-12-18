from django.urls import path
from . import views

urlpatterns = [
    # General
    path('', views.home, name='home'),
    path('logout/', views.user_logout, name='logout'),
    
    # Registro y Activación
    path('registro/', views.registro, name='registro'),
    path('activar/<int:user_id>/<str:token>/', views.activacion_cuenta, name='activacion_cuenta'),
    path('activar/solicitar/', views.solicitar_activacion, name='solicitar_activacion'),
    
    # Login con MFA
    path('login/', views.login_step1, name='login_step1'),
    path('login/mfa/', views.login_step2, name='login_step2'),
    
    # Recuperación de Contraseña
    path('password/recuperar/', views.recuperar_password, name='recuperar_password'),
    path('password/restablecer/<int:user_id>/<str:token>/', views.restablecer_password, name='restablecer_password'),
]