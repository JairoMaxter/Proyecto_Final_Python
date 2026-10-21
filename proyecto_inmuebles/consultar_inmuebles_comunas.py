import os
import django

# 1. Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_inmuebles.settings')
django.setup()

from django.db import connection

def generar_reporte_inmuebles_por_comuna():
    # 2. Consulta SQL pura recuperando solo 'nombre' y 'descripcion' ordenados por comuna
    query = """
        SELECT 
            c.nombre AS comuna_nombre,
            i.nombre AS inmueble_nombre,
            i.descripcion AS inmueble_descripcion
        FROM gestion_inmuebles_inmueble i
        INNER JOIN gestion_inmuebles_comuna c ON i.comuna_id = c.id
        WHERE i.disponible = TRUE
        ORDER BY c.nombre, i.nombre;
    """

    # 3. Ejecutar la consultaSQL usando la conexion de Django
    with connection.cursor() as cursor:
        cursor.execute(query)
        resultados = cursor.fetchall()

    # 4. Procesar y agrupar los datos por comuna
    reporte_comunas = {}
    for comuna, nombre, descripcion in resultados:
        if comuna not in reporte_comunas:
            reporte_comunas[comuna] = []
        reporte_comunas[comuna].append({
            'nombre': nombre,
            'descripcion': descripcion
        })

    # 5. Escribir los resultados en el archivo de texto
    nombre_archivo = "inmuebles_por_comuna.txt"
    
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        archivo.write("==================================================\n")
        archivo.write("   LISTADO DE INMUEBLES EN ARRIENDO POR COMUNA   \n")
        archivo.write("==================================================\n\n")

        if not reporte_comunas:
            archivo.write("No se encontraron inmuebles disponibles para arriendo.\n")
        else:
            for comuna, inmuebles in reporte_comunas.items():
                archivo.write(f"COMUNA: {comuna.upper()}\n")
                archivo.write("-" * 40 + "\n")
                
                for idx, item in enumerate(inmuebles, start=1):
                    archivo.write(f"  {idx}. Nombre: {item['nombre']}\n")
                    archivo.write(f"     Descripción: {item['descripcion']}\n\n")
                
                archivo.write("\n")

    print(f"Reporte generado exitosamente en el archivo '{nombre_archivo}'.")

if __name__ == '__main__':
    generar_reporte_inmuebles_por_comuna()