from functools import wraps

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.urls import reverse
from django.views.decorators.http import require_POST
from .models import (Inmueble, Comuna, Region, TipoInmueble, SolicitudArriendo, PerfilUsuario)
from .forms import InmuebleForm, RegistroUsuarioForm, UserUpdateForm, PerfilUpdateForm


# ==========================================
# 0. UTILIDADES DE PERMISOS
# ==========================================

def arrendador_required(view_func):
    """
    Exige sesión iniciada Y perfil de tipo 'arrendador'.
    Ocultar botones en el template no protege la URL: este chequeo es el real.
    """
    @login_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        perfil = getattr(request.user, 'perfil', None)
        if perfil is None or perfil.tipo_usuario != 'arrendador':
            messages.error(request, "Esta sección es solo para cuentas de arrendador.")
            return redirect('gestion_inmuebles:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped


# ==========================================
# 1. AUTENTICACIÓN Y REGISTRO
# ==========================================

def registro(request):
    """Permite el registro de nuevos usuarios en el sistema."""
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Cuenta creada exitosamente! Ahora puedes iniciar sesión.")
            return redirect('gestion_inmuebles:login')
    else:
        form = RegistroUsuarioForm()
        
    return render(request, 'register.html', {'form': form})


# ==========================================
# 2. VISTAS PÚBLICAS Y NAVEGACIÓN
# ==========================================

def home(request):
    """Vista principal rápida para la portada del sitio."""
    inmuebles = Inmueble.objects.filter(disponible=True)[:9]
    return render(request, 'index.html', {'inmuebles': inmuebles})


def index(request):
    """Página de inicio con filtros avanzados por Región, Comuna, Tipo y Ordenamiento."""
    busqueda = request.GET.get('q', '')
    region_id = request.GET.get('region', '')
    comuna_id = request.GET.get('comuna', '')
    tipo_id = request.GET.get('tipo', '')
    habitaciones = request.GET.get('habitaciones', '')
    banos = request.GET.get('banos', '')
    orden = request.GET.get('orden', '')

    inmuebles = Inmueble.objects.filter(disponible=True)

    # Búsqueda por texto general
    if busqueda:
        inmuebles = inmuebles.filter(
            Q(nombre__icontains=busqueda) |
            Q(descripcion__icontains=busqueda) |
            Q(direccion__icontains=busqueda) |
            Q(comuna__nombre__icontains=busqueda)
        )

    # Filtro por Región
    if region_id:
        inmuebles = inmuebles.filter(comuna__region_id=region_id)
        # Acotamos las comunas de la región seleccionada para el backend
        comunas = Comuna.objects.filter(region_id=region_id)
    else:
        comunas = Comuna.objects.all()

    # Filtro por Comuna específica
    if comuna_id:
        inmuebles = inmuebles.filter(comuna_id=comuna_id)
    
    # Filtro por Tipo de Inmueble
    if tipo_id:
        inmuebles = inmuebles.filter(tipo_inmueble_id=tipo_id)

    # Filtros de características
    if habitaciones:
        inmuebles = inmuebles.filter(habitaciones=habitaciones)
    if banos:
        inmuebles = inmuebles.filter(banos=banos)

    # Ordenamiento
    if orden == 'precio_asc':
        inmuebles = inmuebles.order_by('precio_mensual')
    elif orden == 'precio_desc':
        inmuebles = inmuebles.order_by('-precio_mensual')
    else:
        inmuebles = inmuebles.order_by('-fecha_creacion')

    regiones = Region.objects.all()
    tipos_inmueble = TipoInmueble.objects.all()

    return render(request, 'index.html', {
        'inmuebles': inmuebles,
        'regiones': regiones,
        'comunas': comunas,
        'tipos_inmueble': tipos_inmueble,
        'busqueda_actual': busqueda,
        'region_seleccionada': region_id,
        'comuna_seleccionada': comuna_id,
        'tipo_seleccionado': tipo_id,
        'habitaciones_seleccionadas': habitaciones,
        'banos_seleccionados': banos,
        'orden_seleccionado': orden,
    })

# ==========================================
# 3. DASHBOARD Y PANEL PRIVADO
# ==========================================

@login_required
def dashboard(request):
    """
    Panel de usuario autenticado:
    - Arrendador: Administra sus inmuebles publicados y solicitudes recibidas.
    - Arrendatario: Administra el historial de sus solicitudes realizadas.
    """
    perfil = getattr(request.user, 'perfil', None)
    es_arrendador = perfil is not None and perfil.tipo_usuario == 'arrendador'

    if es_arrendador:
        # Una sola consulta: cada inmueble trae su total de solicitudes y las pendientes
        mis_inmuebles = (
            request.user.inmuebles
            .select_related('comuna', 'tipo_inmueble')
            .annotate(
                total_solicitudes=Count('solicitudes'),
                solicitudes_pendientes=Count('solicitudes', filter=Q(solicitudes__estado='pendiente')),
            )
        )
        solicitudes = (
            SolicitudArriendo.objects
            .filter(inmueble__propietario=request.user)
            .select_related('inmueble', 'arrendatario')
        )
        return render(request, 'dashboard.html', {
            'mis_inmuebles': mis_inmuebles,
            'solicitudes': solicitudes,
            'solicitudes_pendientes': solicitudes.filter(estado='pendiente').count(),
            'es_arrendador': True,
        })

    mis_solicitudes = request.user.solicitudes.select_related('inmueble__comuna')
    return render(request, 'dashboard.html', {
        'mis_solicitudes': mis_solicitudes,
        'es_arrendador': False,
    })


# ==========================================
# 4. OPERACIONES CRUD DE INMUEBLES
# ==========================================

@arrendador_required
def crear_inmueble(request):
    """CREATE: Permite a un arrendador publicar una propiedad."""
    if request.method == 'POST':
        form = InmuebleForm(request.POST)
        if form.is_valid():
            inmueble = form.save(commit=False)
            inmueble.propietario = request.user
            inmueble.save()
            messages.success(request, "Inmueble publicado correctamente.")
            return redirect('gestion_inmuebles:dashboard')
    else:
        form = InmuebleForm()

    return render(request, 'inmueble_form.html', {
        'form': form, 
        'titulo': 'Publicar nuevo inmueble'
    })


@arrendador_required
def editar_inmueble(request, pk):
    """UPDATE: Permite modificar una propiedad del usuario actual."""
    inmueble = get_object_or_404(Inmueble, pk=pk, propietario=request.user)
    
    if request.method == 'POST':
        form = InmuebleForm(request.POST, instance=inmueble)
        if form.is_valid():
            form.save()
            messages.success(request, "Los datos del inmueble han sido actualizados.")
            return redirect('gestion_inmuebles:dashboard')
    else:
        form = InmuebleForm(instance=inmueble)

    return render(request, 'inmueble_form.html', {
        'form': form, 
        'titulo': 'Editar inmueble'
    })


@arrendador_required
def eliminar_inmueble(request, pk):
    """
    DELETE: Elimina una propiedad del usuario actual.
    El dashboard lo hace desde un modal (POST directo); el GET queda como
    página de confirmación para cuando el navegador no tenga JavaScript.
    """
    inmueble = get_object_or_404(Inmueble, pk=pk, propietario=request.user)
    
    if request.method == 'POST':
        inmueble.delete()
        messages.success(request, "El inmueble ha sido eliminado de la plataforma.")
        return redirect('gestion_inmuebles:dashboard')
        
    return render(request, 'inmueble_confirm_delete.html', {
        'inmueble': inmueble
    })

def detalle_inmueble(request, pk):
    inmueble = get_object_or_404(
        Inmueble.objects.select_related('comuna__region', 'tipo_inmueble', 'propietario'),
        pk=pk
    )
    es_propietario = False
    es_arrendatario = False
    ya_solicitado = False

    if request.user.is_authenticated:
        es_propietario = inmueble.propietario_id == request.user.id

        # getattr con default funciona porque la excepción de la relación inversa
        # hereda de AttributeError (mismo patrón que se usa en dashboard)
        perfil = getattr(request.user, 'perfil', None)
        es_arrendatario = perfil is not None and perfil.tipo_usuario == 'arrendatario'

        if es_arrendatario:
            ya_solicitado = SolicitudArriendo.objects.filter(
                inmueble=inmueble, arrendatario=request.user
            ).exists()

    return render(request, 'detalle_inmueble.html', {
        'inmueble': inmueble,
        'ya_solicitado': ya_solicitado,
        'es_arrendatario': es_arrendatario,
        'es_propietario': es_propietario,
    })

# ==========================================
# 5. GESTIÓN DE SOLICITUDES DE ARRIENDO
# ==========================================

@login_required
def solicitar_arriendo(request, pk):
    """Permite a un arrendatario enviar una propuesta de arriendo."""
    inmueble = get_object_or_404(Inmueble, pk=pk, disponible=True)
    detalle = redirect('gestion_inmuebles:detalle_inmueble', pk=pk)

    if request.method != 'POST':
        return detalle

    perfil = getattr(request.user, 'perfil', None)
    if perfil is None or perfil.tipo_usuario != 'arrendatario':
        messages.error(request, "Solo los arrendatarios pueden enviar solicitudes.")
        return detalle

    if inmueble.propietario_id == request.user.id:
        messages.error(request, "No puedes solicitar el arriendo de tu propio inmueble.")
        return detalle

    if SolicitudArriendo.objects.filter(inmueble=inmueble, arrendatario=request.user).exists():
        messages.warning(request, "Ya enviaste una solicitud para este inmueble.")
        return detalle

    SolicitudArriendo.objects.create(
        inmueble=inmueble,
        arrendatario=request.user,
        mensaje=request.POST.get('mensaje', '').strip(),
    )
    messages.success(request, "Solicitud de arriendo enviada al propietario.")
    return redirect('gestion_inmuebles:dashboard')


@arrendador_required
@require_POST
def responder_solicitud(request, pk, estado):
    """
    Permite al propietario aceptar o rechazar solicitudes recibidas.
    Solo por POST: una acción que cambia datos no debe poder dispararse con un enlace.
    """
    solicitud = get_object_or_404(SolicitudArriendo, pk=pk, inmueble__propietario=request.user)

    if estado not in ('aceptada', 'rechazada'):
        messages.error(request, "Estado de solicitud no válido.")
    elif solicitud.estado != 'pendiente':
        messages.warning(request, "Esta solicitud ya fue respondida.")
    else:
        solicitud.estado = estado
        solicitud.save(update_fields=['estado'])
        messages.success(request, f"La solicitud ha sido marcada como '{estado}'.")

    # El ancla devuelve al arrendador a la sección de solicitudes
    return redirect(f"{reverse('gestion_inmuebles:dashboard')}#solicitudes")

# ==========================================
# 6. EDITAR PERFIL DE USUARIO Y VISTA DE PERFIL
# ==========================================

@login_required
def perfil_usuario(request):
    """Vista de perfil de usuario adaptada según su rol (Arrendador o Arrendatario)."""
    perfil, created = PerfilUsuario.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        perfil_form = PerfilUpdateForm(request.POST, instance=perfil)

        if user_form.is_valid() and perfil_form.is_valid():
            user_form.save()
            perfil_form.save()
            messages.success(request, "¡Tus datos de perfil han sido actualizados con éxito!")
            return redirect('gestion_inmuebles:perfil')
        else:
            messages.error(request, "Por favor, corrige los errores. Los campos obligatorios no pueden estar vacíos.")
    else:
        user_form = UserUpdateForm(instance=request.user)
        perfil_form = PerfilUpdateForm(instance=perfil)

    context = {
        'user_form': user_form,
        'perfil_form': perfil_form,
        'perfil': perfil,
    }

    # Lógica condicional según el tipo de usuario
    if perfil.tipo_usuario == 'arrendador':
        # Inmuebles publicados por el arrendador
        context['mis_inmuebles'] = Inmueble.objects.filter(propietario=request.user)
        # Solicitudes recibidas para sus propiedades
        context['solicitudes_recibidas'] = SolicitudArriendo.objects.filter(
            inmueble__propietario=request.user
        ).order_by('-fecha_solicitud')
    else:
        # Solicitudes enviadas por el arrendatario
        context['mis_solicitudes'] = SolicitudArriendo.objects.filter(
            arrendatario=request.user
        ).order_by('-fecha_solicitud')
        # Propiedad arrendada con solicitud aceptada
        context['propiedad_arrendada'] = SolicitudArriendo.objects.filter(
            arrendatario=request.user, 
            estado='aceptada'
        ).first()

    return render(request, 'perfil.html', context)
