import os
import django

# 1. Configurar el entorno de Django para poder usar el ORM desde un script independiente
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_inmuebles.settings')
django.setup()

from gestion_inmuebles.models import Region, Comuna, TipoInmueble, Inmueble, PerfilUsuario
from django.contrib.auth.models import User

def ejecutar_crud_demo():
    print("=" * 60)
    print("DEMOSTRACIÓN DE OPERACIONES CRUD CON EL ORM DE DJANGO")
    print("=" * 60)

    # Aseguramos dependencias mínimas (Región, Comuna, Tipo e Inmueble y Usuario Propietario)
    region, _ = Region.objects.get_or_create(cod="13", defaults={"nombre": "Metropolitana de Santiago"})
    comuna, _ = Comuna.objects.get_or_create(cod="13101", defaults={"nombre": "Santiago", "region": region})
    tipo, _ = TipoInmueble.objects.get_or_create(nombre="Departamento")
    propietario, _ = User.objects.get_or_create(username="demo_propietario", defaults={"email": "demo@example.com"})

    # -------------------------------------------------------------
    # a. CREAR UN OBJETO CON EL MODELO (Create)
    # -------------------------------------------------------------
    print("\n[a] CREAR: Guardando un nuevo inmueble...")
    nuevo_inmueble = Inmueble.objects.create(
        propietario=propietario,
        nombre="Departamento de Prueba Hito 1",
        descripcion="Excelente departamento central para pruebas de CRUD.",
        m2_construidos=50.0,
        m2_totales=55.0,
        estacionamientos=1,
        habitaciones=2,
        banos=1,
        direccion="Av. Libertador Bernardo O'Higgins 1234",
        comuna=comuna,
        tipo_inmueble=tipo,
        precio_mensual=450000.00,
        disponible=True
    )
    print(f"   -> Creado con éxito. ID: {nuevo_inmueble.id} | Nombre: {nuevo_inmueble.nombre}")

    # -------------------------------------------------------------
    # b. ENLISTAR DESDE EL MODELO DE DATOS (Read)
    # -------------------------------------------------------------
    print("\n[b] LISTAR: Consultando inmuebles registrados en la Base de Datos...")
    inmuebles = Inmueble.objects.all()
    for item in inmuebles:
        print(f"   - ID: {item.id} | {item.nombre} | Precio: ${item.precio_mensual:,.0f} | Comuna: {item.comuna.nombre}")

    # -------------------------------------------------------------
    # c. ACTUALIZAR UN REGISTRO EN EL MODELO DE DATOS (Update)
    # -------------------------------------------------------------
    print(f"\n[c] ACTUALIZAR: Modificando precio y descripción del inmueble ID {nuevo_inmueble.id}...")
    inmueble_a_editar = Inmueble.objects.get(id=nuevo_inmueble.id)
    inmueble_a_editar.precio_mensual = 480000.00
    inmueble_a_editar.descripcion = "Excelente departamento central (Precio e información actualizada)."
    inmueble_a_editar.save()
    
    # Verificación de la actualización
    inmueble_actualizado = Inmueble.objects.get(id=nuevo_inmueble.id)
    print(f"   -> Precio actualizado a: ${inmueble_actualizado.precio_mensual:,.0f}")
    print(f"   -> Nueva Descripción: {inmueble_actualizado.descripcion}")

    # -------------------------------------------------------------
    # d. BORRAR UN REGISTRO DEL MODELO DE DATOS (Delete)
    # -------------------------------------------------------------
    print(f"\n[d] ELIMINAR: Borrando el inmueble de prueba ID {nuevo_inmueble.id}...")
    inmueble_a_borrar = Inmueble.objects.get(id=nuevo_inmueble.id)
    inmueble_a_borrar.delete()
    print("   -> Inmueble eliminado con éxito de la base de datos.")

    # Comprobación de eliminación
    existe = Inmueble.objects.filter(id=nuevo_inmueble.id).exists()
    print(f"   -> ¿El inmueble aún existe en la BD?: {existe}")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    ejecutar_crud_demo()