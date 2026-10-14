from django import forms
from .models import Productor, Campo, MarcaSenal, Solicitud, TipoSenal, ImagenMarcaPredefinida
import re
from django.core.validators import RegexValidator


from django import forms
from django.core.validators import RegexValidator
from .models import Productor
from .validators import (
    DNIValidator, CUITValidator, NombreApellidoValidator,
    TelefonoValidator, EmailValidator
)
import re


import re
from django import forms
from .models import Productor
from .validators import (
    DNIValidator,
    CUITValidator,
    NombreApellidoValidator,
    TelefonoValidator,
    EmailValidator
)


class ProductorForm(forms.ModelForm):

    # =========================
    # CAMPOS PERSONALIZADOS
    # =========================
    dni = forms.CharField(
        max_length=8,
        validators=[DNIValidator()],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': 'required',
            'pattern': r'\d{7,8}',
            'title': 'DNI: 7 u 8 números sin puntos ni espacios',
            'placeholder': '12345678',
            'oninput': "this.value = this.value.replace(/[^0-9]/g, '')"
        })
    )

    cuit = forms.CharField(
        required=False,
        validators=[CUITValidator()],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': r'\d{2}-\d{8}-\d{1}',
            'title': 'Formato: 00-00000000-0',
            'placeholder': '20-12345678-9',
            'onkeypress': 'return validarCUIT(event, this)',
            'oninput': 'formatearCUIT(this)'
        })
    )

    nombre = forms.CharField(
        validators=[NombreApellidoValidator()],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': 'required',
            'pattern': r'[A-Za-záéíóúÁÉÍÓÚñÑ\s]+',
            'title': 'Solo letras y espacios',
            'placeholder': 'Juan',
            'onkeypress': 'return soloLetras(event)',
            'oninput': 'capitalizarPrimeraLetra(this)'
        })
    )

    apellido = forms.CharField(
        validators=[NombreApellidoValidator()],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': 'required',
            'pattern': r'[A-Za-záéíóúÁÉÍÓÚñÑ\s]+',
            'title': 'Solo letras y espacios',
            'placeholder': 'Pérez',
            'onkeypress': 'return soloLetras(event)',
            'oninput': 'capitalizarPrimeraLetra(this)'
        })
    )

    telefono = forms.CharField(
        required=False,
        max_length=80,
        validators=[TelefonoValidator()],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': r'[\d\s\-\+\(\)]+',
            'title': 'Ej: 3511234567, (351) 123-4567, +54 351 1234567',
            'placeholder': '3511234567',
            'oninput': 'validarTelefono(this)'
        })
    )

    email = forms.EmailField(
        required=False,
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'usuario@ejemplo.com',
            'title': 'Ejemplo: usuario@dominio.com',
            'oninput': 'validarEmail(this)'
        })
    )

    area_hectareas = forms.DecimalField(
        required=False,
        min_value=0,
        max_value=1_000_000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'placeholder': '0.00'
        })
    )

    # =========================
    # META
    # =========================
    class Meta:
        model = Productor
        fields = [
            'nombre', 'apellido', 'dni', 'cuit', 'calle',
            'localidad', 'municipio', 'departamento', 'provincia',
            'telefono', 'email', 'latitud', 'longitud',
            'area_hectareas', 'estado', 'observaciones'
        ]
        widgets = {
            'calle': forms.TextInput(attrs={'class': 'form-control'}),
            'campo': forms.TextInput(attrs={'class': 'form-control'}),
            'localidad': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'required',
                'pattern': r'[A-Za-záéíóúÁÉÍÓÚñÑ\s]+',
                'title': 'Solo letras y espacios'
            }),
            'municipio': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
            'provincia': forms.TextInput(attrs={
                'class': 'form-control',
                'value': 'Catamarca',
                'readonly': 'readonly'
            }),
            'latitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.00000001',
                'required': 'required',
                'readonly': 'readonly'
            }),
            'longitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.00000001',
                'required': 'required',
                'readonly': 'readonly'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            }),
        }

    # =========================
    # INIT
    # =========================
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Asegurar clase CSS en todos los campos
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

    # =========================
    # LIMPIEZAS
    # =========================
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        return nombre.title() if nombre else nombre

    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido')
        return apellido.title() if apellido else apellido

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')

        if dni:
            dni_limpio = re.sub(r'\D', '', dni)

            qs = Productor.objects.filter(dni=dni_limpio)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise forms.ValidationError(
                    f'Ya existe un productor con DNI {dni_limpio}.',
                    code='duplicate_dni'
                )

            return dni_limpio

        return dni

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        return ' '.join(telefono.split()) if telefono else telefono

    def clean(self):
        cleaned_data = super().clean()
        latitud = cleaned_data.get('latitud')
        longitud = cleaned_data.get('longitud')

        if not latitud or not longitud:
            raise forms.ValidationError(
                'Debe seleccionar una ubicación en el mapa.'
            )

        # Validación geográfica Argentina
        if not (-55 <= latitud <= -21 and -75 <= longitud <= -53):
            raise forms.ValidationError(
                'Las coordenadas deben estar dentro del territorio argentino.'
            )

        return cleaned_data



class CampoForm(forms.ModelForm):
    class Meta:
        model = Campo
        fields = ['nombre', 'area_hectareas', 'distrito', 'departamento', 'latitud', 'longitud', 'observaciones']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'area_hectareas': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'distrito': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
            'latitud': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00000001'}),
            'longitud': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00000001'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


from django import forms
from datetime import date

from .models import (
    MarcaSenal, Campo, TipoSenal, ImagenMarcaPredefinida
)
from .validators import NumeroOrdenValidator


from django import forms
from datetime import date
from .models import MarcaSenal, ImagenMarcaPredefinida, TipoSenal, Campo, Solicitud

class MarcaSenalForm(forms.ModelForm):

    # 🔹 MANY TO MANY
    imagenes_predefinidas = forms.ModelMultipleChoiceField(
        queryset=ImagenMarcaPredefinida.objects.filter(activa=True),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'imagen-checkbox'
        }),
        required=False,
        label="Seleccionar imágenes predefinidas"
    )

    fecha_inscripcion = forms.DateField(
        widget=forms.DateInput(format='%Y-%m-%d', attrs={
            'class': 'form-control',
            'type': 'date',
            'required': 'required',
            'max': date.today().isoformat()
        })
    )

    fecha_vencimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(format='%Y-%m-%d', attrs={
            'class': 'form-control',
            'type': 'date',
            'min': date.today().isoformat()
        })
    )

    descripcion_marca = forms.CharField(
        label='Descripción de la Señal',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'required': 'required',
            'placeholder': 'Describa la señal detalladamente...'
        })
    )

    descripcion_senal = forms.CharField(
        label='Descripción de Marca',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Describa la marca si aplica...'
        })
    )

    valor_sellado = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'placeholder': '0.00'
        })
    )

    # 🔹 Campos de ganado
    def ganado_field():
        return forms.IntegerField(
            required=False,
            min_value=0,
            max_value=100000,
            widget=forms.NumberInput(attrs={
                'class': 'form-control form-control-sm small-input',
                'style': 'max-width: 100px;',
                'value': '0',
                'min': '0'
            })
        )

    vacuno = ganado_field()
    caballar = ganado_field()
    mular = ganado_field()
    asnal = ganado_field()
    ovino = ganado_field()
    cabrio = ganado_field()
    porcino = ganado_field()
    camelidos = ganado_field()

    class Meta:
        model = MarcaSenal

        # 🔥 SACAMOS numero_orden
        exclude = ['numero_orden']

        widgets = {
            'productor': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'campo': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'tipo_tramite': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'tipo_senal': forms.HiddenInput(),
            'tipo_marca': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'imagen_marca': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'imagen_carnet_frente': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'imagen_carnet_dorso': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # tipo_senal oculto, se usa tipo_marca en su lugar

        self.fields['imagenes_predefinidas'].queryset = (
            ImagenMarcaPredefinida.objects.filter(activa=True)
        )

        # Filtrar campos por productor
        if 'productor' in self.data:
            try:
                productor_id = int(self.data.get('productor'))
                self.fields['campo'].queryset = Campo.objects.filter(
                    productor_id=productor_id
                )
            except (ValueError, TypeError):
                self.fields['campo'].queryset = Campo.objects.none()
        elif self.instance.pk and self.instance.productor:
            self.fields['campo'].queryset = self.instance.productor.campos.all()
        else:
            self.fields['campo'].queryset = Campo.objects.none()

        self.fields['campo'].help_text = 'Primero seleccione un productor'
        self.fields['valor_sellado'].help_text = 'Valor en pesos argentinos'
        self.fields['descripcion_marca'].help_text = 'Mínimo 10 caracteres'

    def clean_fecha_vencimiento(self):
        fecha_inscripcion = self.cleaned_data.get('fecha_inscripcion')
        fecha_vencimiento = self.cleaned_data.get('fecha_vencimiento')

        if fecha_vencimiento and fecha_inscripcion:
            if fecha_vencimiento <= fecha_inscripcion:
                raise forms.ValidationError(
                    'La fecha de vencimiento debe ser posterior a la fecha de inscripción.'
                )
        return fecha_vencimiento
    
    def clean_imagen_marca(self):
        imagen = self.cleaned_data.get('imagen_marca')
        # Solo validar si es una imagen nueva (no una URL/string de archivo existente)
        if imagen and hasattr(imagen, 'read'):
            from app_registros.validators import ImagenDuplicadaValidator
            validar = ImagenDuplicadaValidator(
                excluir_id=self.instance.pk if self.instance.pk else None
            )
            validar(imagen)
        return imagen

    def clean(self):
        cleaned_data = super().clean()

        descripcion = cleaned_data.get('descripcion_marca', '')
        if len(descripcion.strip()) < 10:
            self.add_error(
                'descripcion_marca',
                'La descripción debe tener al menos 10 caracteres.'
            )

        tipos = ['vacuno', 'caballar', 'mular', 'asnal', 'ovino', 'cabrio']
        total = sum(cleaned_data.get(t, 0) or 0 for t in tipos)

        if total <= 0:
            raise forms.ValidationError(
                'Debe especificar al menos un animal.'
            )

        return cleaned_data



from django import forms
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from datetime import timedelta
from .models import Solicitud, MarcaSenal


class SolicitudForm(forms.ModelForm):

    motivo = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'required': 'required',
            'placeholder': 'Describa el motivo de la solicitud...',
            'minlength': '20',
            'title': 'Mínimo 20 caracteres'
        })
    )

    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Observaciones adicionales...'
        })
    )

    fecha_vencimiento = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )

    documento_adjunto = forms.FileField(
        required=False,
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx']
        )],
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx'
        })
    )

    class Meta:
        model = Solicitud
        fields = [
            'productor',
            'tipo_tramite',
            'marca_senal',
            'productor_destino',
            'prioridad',
            'motivo',
            'observaciones',
            'documento_adjunto',
            'imagen_adicional_1',
            'imagen_adicional_2',
            'fecha_vencimiento',
            'descripcion_marca_nueva',
            'descripcion_senal_nueva',
            'tipo_marca_nueva',
        ]
        widgets = {
            'productor': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'tipo_tramite': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'marca_senal': forms.Select(attrs={
                'class': 'form-control'
            }),
            'productor_destino': forms.Select(attrs={
                'class': 'form-control'
            }),
            'prioridad': forms.Select(attrs={
                'class': 'form-control'
            }),
            'imagen_adicional_1': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'imagen_adicional_2': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'descripcion_marca_nueva': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Nueva descripción de la marca propuesta...'
            }),
            'descripcion_senal_nueva': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Nueva descripción de la señal propuesta...'
            }),
            'tipo_marca_nueva': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

    # ==============================
    # INIT CORREGIDO
    # ==============================
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filtrar marcas según productor seleccionado
        if 'productor' in self.data:
            try:
                productor_id = int(self.data.get('productor'))
                self.fields['marca_senal'].queryset = MarcaSenal.objects.filter(
                    productor_id=productor_id
                )
            except (ValueError, TypeError):
                self.fields['marca_senal'].queryset = MarcaSenal.objects.none()
        elif self.instance.pk and self.instance.productor:
            self.fields['marca_senal'].queryset = (
                self.instance.productor.marcas_senales.all()
            )
        else:
            self.fields['marca_senal'].queryset = MarcaSenal.objects.none()

        # Fecha vencimiento por defecto (solo al crear)
        if not self.instance.pk:
            self.fields['fecha_vencimiento'].initial = (
                timezone.now() + timedelta(days=7)
            )

    # ==============================
    # VALIDACIONES
    # ==============================
    def clean(self):
        cleaned_data = super().clean()
        tipo_tramite = cleaned_data.get('tipo_tramite')
        marca_senal = cleaned_data.get('marca_senal')
        fecha_vencimiento = cleaned_data.get('fecha_vencimiento')
        documento_adjunto = cleaned_data.get('documento_adjunto')

        # Validación de marca/señal obligatoria según tipo
        if tipo_tramite in ['RENOVACION', 'RENOVACION_TRANSFERENCIA', 'RENOVACION_MOD_SENALES', 'TRANSFERENCIA_MOD_SENAL', 'DUPLICADO', 'BAJA']:
            if not marca_senal:
                self.add_error(
                    'marca_senal',
                    'Para este tipo de trámite debe seleccionar una marca/señal.'
                )

        # Validación de productor destino para transferencias
        if tipo_tramite in ['RENOVACION_TRANSFERENCIA', 'TRANSFERENCIA_MOD_SENAL']:
            productor_destino = cleaned_data.get('productor_destino')
            productor_origen = cleaned_data.get('productor')
            if not productor_destino:
                self.add_error(
                    'productor_destino',
                    'Debe indicar el productor al que se transfiere la marca.'
                )
            elif productor_origen and productor_destino == productor_origen:
                self.add_error(
                    'productor_destino',
                    'El productor destino debe ser distinto al productor actual.'
                )

        # Validar fecha futura
        if fecha_vencimiento and fecha_vencimiento < timezone.now():
            self.add_error(
                'fecha_vencimiento',
                'La fecha de vencimiento debe ser futura.'
            )

        # Validar tamaño archivo (10MB)
        if documento_adjunto:
            if documento_adjunto.size > 10 * 1024 * 1024:
                self.add_error(
                    'documento_adjunto',
                    'El documento no puede superar los 10MB.'
                )

        return cleaned_data

    # ==============================
    # SAVE CORREGIDO
    # ==============================
    def save(self, commit=True):
        solicitud = super().save(commit=False)

        # Asignar solicitante si es nueva
        if not solicitud.pk and self.user:
            solicitud.solicitante = self.user

        if commit:
            solicitud.save()
            self.save_m2m()

        return solicitud


# Formulario para revisión de solicitudes
class SolicitudRevisionForm(forms.ModelForm):
    class Meta:
        model = Solicitud
        fields = ['estado', 'observaciones_internas', 'fecha_vencimiento']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'observaciones_internas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Observaciones internas para el revisor...'
            }),
            'fecha_vencimiento': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }



from django import forms
from .models import DocumentoSolicitud

class DocumentoSolicitudForm(forms.ModelForm):
    class Meta:
        model = DocumentoSolicitud
        fields = ['tipo_documento', 'nombre', 'archivo', 'observaciones']
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

# Formset para múltiples documentos
DocumentoSolicitudFormSet = forms.inlineformset_factory(
    Solicitud,
    DocumentoSolicitud,
    form=DocumentoSolicitudForm,
    extra=1,
    can_delete=True,
    max_num=10
)
