import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_inmuebles.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from gestion_inmuebles.models import Inmueble, SolicitudArriendo

def crear_grupos_y_permisos():
    # 1. Grupo Arrendadores
    grupo_arrendadores, _ = Group.objects.get_or_create(name='Arrendadores')
    content_type_inmueble = ContentType.objects.get_for_model(Inmueble)
    
    permisos_arrendador = Permission.objects.filter(content_type=content_type_inmueble)
    grupo_arrendadores.permissions.set(permisos_arrendador)

    # 2. Grupo Arrendatarios
    grupo_arrendatarios, _ = Group.objects.get_or_create(name='Arrendatarios')
    content_type_solicitud = ContentType.objects.get_for_model(SolicitudArriendo)
    
    permisos_arrendatario = Permission.objects.filter(content_type=content_type_solicitud)
    grupo_arrendatarios.permissions.set(permisos_arrendatario)

    print("Grupos 'Arrendadores' y 'Arrendatarios' configurados con sus permisos correctamente.")

if __name__ == '__main__':
    crear_grupos_y_permisos()