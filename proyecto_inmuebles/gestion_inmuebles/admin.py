from django.contrib import admin
from django.utils import timezone
from .models import Region, Comuna, TipoInmueble, PerfilUsuario, Inmueble, SolicitudArriendo


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('cod', 'nombre')
    search_fields = ('nombre', 'cod')


@admin.register(Comuna)
class ComunaAdmin(admin.ModelAdmin):
    list_display = ('cod', 'nombre', 'region')
    search_fields = ('nombre', 'cod')
    list_filter = ('region',)


@admin.register(TipoInmueble)
class TipoInmuebleAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'rut', 'telefono', 'tipo_usuario', 'direccion')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'rut')
    list_filter = ('tipo_usuario',)


@admin.register(Inmueble)
class InmuebleAdmin(admin.ModelAdmin):
    # Columnas visibles en la lista
    list_display = (
        'nombre', 
        'direccion', 
        'comuna', 
        'precio_mensual', 
        'disponible', 
        'fecha_creacion'
    )
    
    # Campos por los que se puede buscar
    search_fields = ('nombre', 'direccion', 'propietario__username')
    
    # Filtros laterales en el panel de administración
    list_filter = ('disponible', 'tipo_inmueble', 'comuna__region', 'comuna')
    
    # Campos de solo lectura
    readonly_fields = ('fecha_creacion',)

    def save_model(self, request, obj, form, change):
        """
        Garantiza que fecha_creacion se asigne correctamente al momento de crear el registro.
        Note: En Django, si usas auto_now_add=True en el modelo para fecha_creacion,
        Django maneja la asignación automáticamente.
        """
        if not change:
            obj.fecha_creacion = timezone.now()
        obj.save()


@admin.register(SolicitudArriendo)
class SolicitudArriendoAdmin(admin.ModelAdmin):
    list_display = ('inmueble', 'arrendatario', 'estado', 'fecha_solicitud')
    search_fields = ('inmueble__nombre', 'arrendatario__username')
    list_filter = ('estado', 'fecha_solicitud')
    list_editable = ('estado',)  # Permite cambiar el estado de la solicitud directamente desde la vista de lista