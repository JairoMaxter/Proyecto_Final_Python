import os
import django

# 1. Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_inmuebles.settings')
django.setup()

from django.db import connection

def generar_reporte_inmuebles_por_region():
    # 2. Consulta SQL pura uniendo Inmueble -> Comuna -> Región
    query = """
        SELECT 
            r.nombre AS region_nombre,
            c.nombre AS comuna_nombre,
            i.nombre AS inmueble_nombre,
            i.descripcion AS inmueble_descripcion
        FROM gestion_inmuebles_inmueble i
        INNER JOIN gestion_inmuebles_comuna c ON i.comuna_id = c.id
        INNER JOIN gestion_inmuebles_region r ON c.region_id = r.id
        WHERE i.disponible = TRUE
        ORDER BY r.nombre, c.nombre, i.nombre;
    """

    # 3. Ejecutar la consulta SQL usando la conexión de Django
    with connection.cursor() as cursor:
        cursor.execute(query)
        resultados = cursor.fetchall()

    # 4. Procesar y agrupar los datos estructuradamente por Región y Comuna
    reporte_regiones = {}
    for region, comuna, nombre, descripcion in resultados:
        if region not in reporte_regiones:
            reporte_regiones[region] = {}
        if comuna not in reporte_regiones[region]:
            reporte_regiones[region][comuna] = []
            
        reporte_regiones[region][comuna].append({
            'nombre': nombre,
            'descripcion': descripcion
        })

    # 5. Escribir los resultados en el archivo de texto
    nombre_archivo = "inmuebles_por_region.txt"
    
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        archivo.write("==================================================\n")
        archivo.write("   LISTADO DE INMUEBLES EN ARRIENDO POR REGIÓN   \n")
        archivo.write("==================================================\n\n")

        if not reporte_regiones:
            archivo.write("No se encontraron inmuebles disponibles para arriendo.\n")
        else:
            for region, comunas_dict in reporte_regiones.items():
                archivo.write(f"REGIÓN: {region.upper()}\n")
                archivo.write("=" * 50 + "\n")
                
                for comuna, inmuebles in comunas_dict.items():
                    archivo.write(f"  [Comuna: {comuna}]\n")
                    for idx, item in enumerate(inmuebles, start=1):
                        archivo.write(f"    {idx}. Nombre: {item['nombre']}\n")
                        archivo.write(f"       Descripción: {item['descripcion']}\n")
                    archivo.write("\n")
                
                archivo.write("\n")

    print(f"Reporte por región generado exitosamente en el archivo '{nombre_archivo}'.")

if __name__ == '__main__':
    generar_reporte_inmuebles_por_region()