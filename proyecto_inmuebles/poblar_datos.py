import os
import django
import random

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_inmuebles.settings')
django.setup()

from django.contrib.auth.models import User
from gestion_inmuebles.models import Region, Comuna, TipoInmueble, PerfilUsuario, Inmueble

def poblar_sistema():
    print("Iniciando poblamiento de datos de prueba...")

    # 1. Crear Regiones
    regiones_data = [
        {"cod": "13", "nombre": "Región Metropolitana de Santiago"},
        {"cod": "05", "nombre": "Región de Valparaíso"},
        {"cod": "08", "nombre": "Región del Biobío"},
    ]
    
    regiones_objs = []
    for r in regiones_data:
        reg, _ = Region.objects.get_or_create(cod=r["cod"], defaults={"nombre": r["nombre"]})
        regiones_objs.append(reg)

    # 2. Crear Comunas
    comunas_data = [
        {"cod": "13101", "nombre": "Santiago", "region": regiones_objs[0]},
        {"cod": "13114", "nombre": "Las Condes", "region": regiones_objs[0]},
        {"cod": "13123", "nombre": "Providencia", "region": regiones_objs[0]},
        {"cod": "05101", "nombre": "Valparaíso", "region": regiones_objs[1]},
        {"cod": "05109", "nombre": "Viña del Mar", "region": regiones_objs[1]},
        {"cod": "08101", "nombre": "Concepción", "region": regiones_objs[2]},
    ]
    
    comunas_objs = []
    for c in comunas_data:
        com, _ = Comuna.objects.get_or_create(cod=c["cod"], defaults={"nombre": c["nombre"], "region": c["region"]})
        comunas_objs.append(com)

    # 3. Crear Tipos de Inmueble
    tipos_data = ["Casa", "Departamento", "Parcela", "Oficina", "Bodega"]
    tipos_objs = []
    for t in tipos_data:
        tipo, _ = TipoInmueble.objects.get_or_create(nombre=t)
        tipos_objs.append(tipo)

    # 4. Crear Usuarios (Propietarios)
    propietarios_data = [
        {"username": "carlos_mora", "first_name": "Carlos", "last_name": "Mora", "email": "carlos@ejemplo.cl", "rut": "15234567-8"},
        {"username": "ana_silva", "first_name": "Ana", "last_name": "Silva", "email": "ana@ejemplo.cl", "rut": "16789123-4"},
        {"username": "roberto_gomez", "first_name": "Roberto", "last_name": "Gómez", "email": "roberto@ejemplo.cl", "rut": "14567890-1"},
    ]

    propietarios_objs = []
    for p in propietarios_data:
        user, created = User.objects.get_or_create(
            username=p["username"],
            defaults={
                "first_name": p["first_name"],
                "last_name": p["last_name"],
                "email": p["email"],
            }
        )
        if created:
            user.set_password("clave1234")
            user.save()
            PerfilUsuario.objects.get_or_create(
                user=user,
                defaults={
                    "rut": p["rut"],
                    "direccion": "Av. Principal 123",
                    "telefono": "+56 9 8765 4321",
                    "tipo_usuario": "arrendador"
                }
            )
        propietarios_objs.append(user)

    # 5. Crear Inmuebles de prueba
    titulos_ejemplo = [
        "Luminoso Departamento Central",
        "Hermosa Casa Familiar con Jardín",
        "Moderna Oficina Comercial",
        "Departamento Studio para Estudiantes",
        "Amplia Parcela de Agrado",
        "Penthouse con Vista Panorámica",
        "Casa Condominio Cerrado",
        "Loft de Estilo Industrial",
        "Oficina Ejecutiva Sector Financiero",
        "Departamento Amoblado Full"
    ]

    calles = [
        "Av. Libertador Bernardo O'Higgins", "Av. Providencia", "Av. Apoquindo",
        "Calle Alvarez", "Av. Alemania", "Av. Pedro de Valdivia", "Calle Esmeralda"
    ]

    for i in range(1, 12):
        comuna_sel = random.choice(comunas_objs)
        tipo_sel = random.choice(tipos_objs)
        prop_sel = random.choice(propietarios_objs)
        titulo = f"{random.choice(titulos_ejemplo)} #{i}"
        
        Inmueble.objects.create(
            propietario=prop_sel,
            nombre=titulo,
            descripcion=f"Excelente propiedad ubicada en {comuna_sel.nombre}. Excelente conectividad y finas terminaciones.",
            m2_construidos=random.randint(45, 220),
            m2_totales=random.randint(50, 500),
            estacionamientos=random.randint(0, 2),
            habitaciones=random.randint(1, 4),
            banos=random.randint(1, 3),
            direccion=f"{random.choice(calles)} #{random.randint(100, 4500)}",
            comuna=comuna_sel,
            tipo_inmueble=tipo_sel,
            precio_mensual=random.choice([350000, 480000, 620000, 850000, 1200000, 1500000]),
            disponible=random.choice([True, True, True, False])
        )

    print("¡Datos generados con éxito!")

if __name__ == '__main__':
    poblar_sistema()