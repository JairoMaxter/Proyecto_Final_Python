from gestion_inmuebles.models import Region, Comuna, TipoInmueble, PerfilUsuario, Inmueble, SolicitudArriendo
from django.contrib.auth.models import User

# ==========================================
# 1. CRUD REGION
# ==========================================

def crea_region(cod, nombre):
    region = Region(cod=cod, nombre=nombre)
    region.save()
    return region

def listar_regiones():
    return Region.objects.all()

def actualiza_region(cod_region, nuevo_nombre):
    region = Region.objects.get(cod=cod_region)
    region.nombre = nuevo_nombre
    region.save()
    return region

def elimina_region(cod_region):
    region = Region.objects.get(cod=cod_region)
    region.delete()


# ==========================================
# 2. CRUD COMUNA
# ==========================================

def crea_comuna(cod, nombre, cod_region):
    region = Region.objects.get(cod=cod_region)
    comuna = Comuna(cod=cod, nombre=nombre, region=region)
    comuna.save()
    return comuna

def listar_comunas():
    return Comuna.objects.all()

def actualiza_comuna(cod_comuna, nuevo_nombre):
    comuna = Comuna.objects.get(cod=cod_comuna)
    comuna.nombre = nuevo_nombre
    comuna.save()
    return comuna

def elimina_comuna(cod_comuna):
    comuna = Comuna.objects.get(cod=cod_comuna)
    comuna.delete()


# ==========================================
# 3. CRUD TIPO INMUEBLE
# ==========================================

def crea_tipo_inmueble(nombre):
    tipo = TipoInmueble(nombre=nombre)
    tipo.save()
    return tipo

def listar_tipos_inmuebles():
    return TipoInmueble.objects.all()

def actualiza_tipo_inmueble(id_tipo, nuevo_nombre):
    tipo = TipoInmueble.objects.get(id=id_tipo)
    tipo.nombre = nuevo_nombre
    tipo.save()
    return tipo

def elimina_tipo_inmueble(id_tipo):
    tipo = TipoInmueble.objects.get(id=id_tipo)
    tipo.delete()


# ==========================================
# 4. CRUD PERFIL USUARIO
# ==========================================

def crea_perfil_usuario(datos_usuario, datos_perfil):
    # datos_usuario = {'username': '...', 'email': '...', 'password': '...', 'first_name': '...', 'last_name': '...'}
    user = User.objects.create_user(**datos_usuario)
    perfil = PerfilUsuario(
        user=user,
        rut=datos_perfil['rut'],
        direccion=datos_perfil['direccion'],
        telefono=datos_perfil['telefono'],
        tipo_usuario=datos_perfil['tipo_usuario']
    )
    perfil.save()
    return perfil

def listar_perfiles_usuarios():
    return PerfilUsuario.objects.all()

def actualiza_perfil_usuario(rut, datos_actualizados):
    perfil = PerfilUsuario.objects.get(rut=rut)
    if 'direccion' in datos_actualizados:
        perfil.direccion = datos_actualizados['direccion']
    if 'telefono' in datos_actualizados:
        perfil.telefono = datos_actualizados['telefono']
    if 'tipo_usuario' in datos_actualizados:
        perfil.tipo_usuario = datos_actualizados['tipo_usuario']
    perfil.save()
    return perfil

def elimina_perfil_usuario(rut):
    perfil = PerfilUsuario.objects.get(rut=rut)
    user = perfil.user
    perfil.delete()
    user.delete()  # Elimina el usuario asociado en la tabla auth_user


# ==========================================
# 5. CRUD INMUEBLE
# ==========================================

def crea_inmueble(datos):
    obj_inmueble = Inmueble(
        nombre=datos['nombre'],
        descripcion=datos['descripcion'],
        m2_construidos=datos['m2_construidos'],
        m2_totales=datos['m2_totales'],
        estacionamientos=datos['estacionamientos'],
        habitaciones=datos['habitaciones'],
        banos=datos['banos'],
        direccion=datos['direccion'],
        comuna_id=datos['comuna_id'],
        tipo_inmueble_id=datos['tipo_inmueble_id'],
        precio_mensual=datos['precio_mensual'],
        propietario_id=datos['id_propietario']
    )
    obj_inmueble.save()
    return obj_inmueble

def listar_inmuebles():
    return Inmueble.objects.all()

def actualiza_inmueble(id_inmueble, datos_actualizados):
    inmueble = Inmueble.objects.get(id=id_inmueble)
    for clave, valor in datos_actualizados.items():
        setattr(inmueble, clave, valor)
    inmueble.save()
    return inmueble

def elimina_inmueble(id_inmueble):
    inmueble = Inmueble.objects.get(id=id_inmueble)
    inmueble.delete()


# ==========================================
# 6. CRUD SOLICITUD DE ARRIENDO
# ==========================================

def crea_solicitud_arriendo(id_inmueble, id_arrendatario, mensaje=""):
    solicitud = SolicitudArriendo(
        inmueble_id=id_inmueble,
        arrendatario_id=id_arrendatario,
        mensaje=mensaje,
        estado='pendiente'
    )
    solicitud.save()
    return solicitud

def listar_solicitudes_arriendo():
    return SolicitudArriendo.objects.all()

def actualiza_estado_solicitud(id_solicitud, nuevo_estado):
    solicitud = SolicitudArriendo.objects.get(id=id_solicitud)
    solicitud.estado = nuevo_estado
    solicitud.save()
    return solicitud

def elimina_solicitud_arriendo(id_solicitud):
    solicitud = SolicitudArriendo.objects.get(id=id_solicitud)
    solicitud.delete()