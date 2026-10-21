from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import PerfilUsuario, Inmueble, Region

class RegistroUsuarioForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True, label="Nombres")
    last_name = forms.CharField(max_length=150, required=True, label="Apellidos")
    email = forms.EmailField(required=True, label="Correo Electrónico")
    
    rut = forms.CharField(max_length=12, required=True, label="RUT")
    direccion = forms.CharField(max_length=255, required=True, label="Dirección")
    telefono = forms.CharField(max_length=20, required=True, label="Teléfono Personal")
    tipo_usuario = forms.ChoiceField(
        choices=PerfilUsuario.TIPO_USUARIO_CHOICES, 
        required=True, 
        label="Tipo de Usuario"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            PerfilUsuario.objects.create(
                user=user,
                rut=self.cleaned_data['rut'],
                direccion=self.cleaned_data['direccion'],
                telefono=self.cleaned_data['telefono'],
                tipo_usuario=self.cleaned_data['tipo_usuario']
            )
        return user

class ComunaSelect(forms.Select):
    """
    Select de comunas que agrega data-region a cada <option>.
    El formulario usa ese atributo para mostrar solo las comunas de la región elegida.
    """
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        instance = getattr(value, 'instance', None)  # la opción vacía no tiene instancia
        if instance is not None:
            option['attrs']['data-region'] = instance.region_id
        return option


class InmuebleForm(forms.ModelForm):
    # Campo auxiliar (no se guarda en Inmueble): solo sirve para filtrar las comunas.
    region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        label="Región",
        empty_label="Selecciona una región",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    # La región va justo antes de la comuna
    field_order = [
        'nombre', 'descripcion', 'm2_construidos', 'm2_totales', 'estacionamientos',
        'habitaciones', 'banos', 'direccion', 'region', 'comuna', 'tipo_inmueble',
        'precio_mensual', 'disponible',
    ]

    class Meta:
        model = Inmueble
        fields = [
            'nombre',
            'descripcion',
            'm2_construidos',
            'm2_totales',
            'estacionamientos',
            'habitaciones',
            'banos',
            'direccion',
            'comuna',
            'tipo_inmueble',
            'precio_mensual',
            'disponible',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'm2_construidos': forms.NumberInput(attrs={'class': 'form-control'}),
            'm2_totales': forms.NumberInput(attrs={'class': 'form-control'}),
            'estacionamientos': forms.NumberInput(attrs={'class': 'form-control'}),
            'habitaciones': forms.NumberInput(attrs={'class': 'form-control'}),
            'banos': forms.NumberInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'comuna': ComunaSelect(attrs={'class': 'form-select'}),
            'tipo_inmueble': forms.Select(attrs={'class': 'form-select'}),
            'precio_mensual': forms.NumberInput(attrs={'class': 'form-control'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # La región se elige aparte, así que cada comuna se muestra solo con su nombre
        # (además evita una consulta por comuna para leer su región).
        self.fields['comuna'].label_from_instance = lambda comuna: comuna.nombre
        self.fields['comuna'].empty_label = "Selecciona una comuna"
        # Al editar, la región parte con la de la comuna actual
        if self.instance.pk:
            self.fields['region'].initial = self.instance.comuna.region_id

    def clean(self):
        cleaned_data = super().clean()
        region = cleaned_data.get('region')
        comuna = cleaned_data.get('comuna')
        # Sin JavaScript el select de comunas muestra todas: la validación real es esta
        if region and comuna and comuna.region_id != region.pk:
            self.add_error('comuna', "La comuna seleccionada no pertenece a la región elegida.")
        return cleaned_data


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Correo Electrónico")
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class PerfilUpdateForm(forms.ModelForm):
    telefono = forms.CharField(required=True, label="Teléfono de Contacto")
    
    class Meta:
        model = PerfilUsuario
        fields = ['telefono', 'direccion']
        widgets = {
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
        }