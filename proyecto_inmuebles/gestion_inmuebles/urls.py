from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'gestion_inmuebles'

urlpatterns = [
    # Público
    path('', views.index, name='index'),
    path('detalle/<int:pk>/', views.detalle_inmueble, name='detalle_inmueble'),

    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('register/', views.registro, name='register'),

    # Panel privado
    path('dashboard/', views.dashboard, name='dashboard'),
    path('perfil/', views.perfil_usuario, name='perfil'),

    # CRUD de inmuebles
    path('inmueble/crear/', views.crear_inmueble, name='crear_inmueble'),
    path('inmueble/<int:pk>/editar/', views.editar_inmueble, name='editar_inmueble'),
    path('inmueble/<int:pk>/eliminar/', views.eliminar_inmueble, name='eliminar_inmueble'),

    # Solicitudes de arriendo
    path('solicitar/<int:pk>/', views.solicitar_arriendo, name='solicitar_arriendo'),
    path('solicitud/responder/<int:pk>/<str:estado>/', views.responder_solicitud, name='responder_solicitud'),
]