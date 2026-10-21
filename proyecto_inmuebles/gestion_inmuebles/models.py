from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

# ==========================================
# 1. MODELOS GEOGRÁFICOS Y TIPOS
# ==========================================

class Region(models.Model):
    cod = models.CharField(max_length=5, unique=True, verbose_name="Código de Región")
    nombre = models.CharField(max_length=100, verbose_name="Nombre de Región")

    class Meta:
        verbose_name = "Región"
        verbose_name_plural = "Regiones"
        ordering = ['cod']

    def __str__(self):
        return self.nombre


class Comuna(models.Model):
    cod = models.CharField(max_length=10, unique=True, verbose_name="Código de Comuna")
    nombre = models.CharField(max_length=100, verbose_name="Nombre de Comuna")
    region = models.ForeignKey(
        Region, 
        on_delete=models.CASCADE, 
        related_name='comunas',
        verbose_name="Región"
    )

    class Meta:
        verbose_name = "Comuna"
        verbose_name_plural = "Comunas"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.region.nombre})"


class TipoInmueble(models.Model):
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Tipo de Inmueble")

    class Meta:
        verbose_name = "Tipo de Inmueble"
        verbose_name_plural = "Tipos de Inmuebles"

    def __str__(self):
        return self.nombre

# ==========================================
# 2. PERFIL DE USUARIO
# ==========================================

class PerfilUsuario(models.Model):
    TIPO_USUARIO_CHOICES = [
        ('arrendatario', 'Arrendatario'),
        ('arrendador', 'Arrendador'),
    ]

    # Relación 1 a 1 con el modelo integrado User de Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rut = models.CharField(max_length=12, unique=True, verbose_name="RUT")
    direccion = models.CharField(max_length=255, verbose_name="Dirección")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono Personal")
    tipo_usuario = models.CharField(
        max_length=20, 
        choices=TIPO_USUARIO_CHOICES, 
        default='arrendatario',
        verbose_name="Tipo de Usuario"
    )

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.get_tipo_usuario_display()})"

# ==========================================
# 3. MODELO DE INMUEBLE
# ==========================================

class Inmueble(models.Model):
    # Relación con el arrendador (Propietario)
    propietario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='inmuebles',
        verbose_name="Propietario (Arrendador)"
    )
    nombre = models.CharField(max_length=200, verbose_name="Nombre / Título")
    descripcion = models.TextField(verbose_name="Descripción")
    m2_construidos = models.FloatField(validators=[MinValueValidator(0.0)], verbose_name="m² Construidos")
    m2_totales = models.FloatField(validators=[MinValueValidator(0.0)], verbose_name="m² Totales del Terreno")
    estacionamientos = models.PositiveIntegerField(default=0, verbose_name="Cantidad de Estacionamientos")
    habitaciones = models.PositiveIntegerField(default=1, verbose_name="Cantidad de Habitaciones")
    banos = models.PositiveIntegerField(default=1, verbose_name="Cantidad de Baños")
    direccion = models.CharField(max_length=255, verbose_name="Dirección")
    
    # Claves Foráneas requeridas
    comuna = models.ForeignKey(
        Comuna, 
        on_delete=models.CASCADE, 
        related_name='inmuebles',
        verbose_name="Comuna"
    )
    tipo_inmueble = models.ForeignKey(
        TipoInmueble, 
        on_delete=models.PROTECT, 
        related_name='inmuebles',
        verbose_name="Tipo de Inmueble"
    )
    
    precio_mensual = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Precio Mensual de Arriendo ($)")
    disponible = models.BooleanField(default=True, verbose_name="¿Está Disponible?")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Inmueble"
        verbose_name_plural = "Inmuebles"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre} - {self.comuna.nombre} (${self.precio_mensual:,.0f})"

# ==========================================
# 4. SOLICITUDES DE ARRIENDO
# ==========================================

class SolicitudArriendo(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
    ]

    inmueble = models.ForeignKey(
        Inmueble, 
        on_delete=models.CASCADE, 
        related_name='solicitudes',
        verbose_name="Inmueble"
    )
    arrendatario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='solicitudes',
        verbose_name="Arrendatario"
    )
    mensaje = models.TextField(blank=True, null=True, verbose_name="Mensaje para el Arrendador")
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='pendiente',
        verbose_name="Estado de Solicitud"
    )
    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Solicitud de Arriendo"
        verbose_name_plural = "Solicitudes de Arriendo"
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"Solicitud de {self.arrendatario.username} para {self.inmueble.nombre} [{self.estado}]"