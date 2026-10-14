from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re

class DNIValidator:
    """
    Validador de DNI argentino (7-8 dígitos)
    """
    def __call__(self, value):
        if not value:
            return
        
        # Remover puntos, espacios y guiones
        dni_limpio = str(value).replace('.', '').replace(' ', '').replace('-', '')
        
        # Validar que solo contenga números
        if not dni_limpio.isdigit():
            raise ValidationError(
                _('El DNI debe contener solo números (sin puntos ni espacios).'),
                code='invalid_dni'
            )
        
        # Validar longitud (7-8 dígitos)
        if len(dni_limpio) < 7 or len(dni_limpio) > 8:
            raise ValidationError(
                _('El DNI debe tener entre 7 y 8 dígitos.'),
                code='invalid_dni_length'
            )
        
        return dni_limpio

class CUITValidator:
    """
    Validador de CUIT/CUIL argentino (formato: 00-00000000-0)
    """
    def __call__(self, value):
        if not value:
            return
        
        pattern = r'^\d{2}-\d{8}-\d{1}$'
        
        if not re.match(pattern, str(value)):
            raise ValidationError(
                _('El CUIT debe tener el formato: 00-00000000-0 (11 dígitos con guiones).'),
                code='invalid_cuit_format'
            )
        
        try:
            cuit = str(value).replace('-', '')
            coeficientes = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
            
            suma = sum(int(cuit[i]) * coeficientes[i] for i in range(10))
            resto = suma % 11
            resultado = 11 - resto
            
            if resultado == 11:
                digito_calculado = 0
            elif resultado == 10:
                digito_calculado = 9  # simplificado
            else:
                digito_calculado = resultado
            
            if digito_calculado != int(cuit[10]):
                raise ValidationError(
                    _('El CUIT no es válido (dígito verificador incorrecto).'),
                    code='invalid_cuit_dv'
                )
        
        except (IndexError, ValueError):
            raise ValidationError(
                _('El CUIT no es válido.'),
                code='invalid_cuit'
            )
        
        return value


class NombreApellidoValidator:
    """
    Validador de nombres y apellidos (solo letras y espacios)
    """
    def __call__(self, value):
        if not value:
            return
        
        # Permitir letras, espacios, tildes y ñ
        if not re.match(r'^[A-Za-záéíóúÁÉÍÓÚñÑ\s]+$', str(value)):
            raise ValidationError(
                _('Solo se permiten letras y espacios.'),
                code='invalid_chars'
            )
        
        # Mínimo 2 caracteres
        if len(str(value).strip()) < 2:
            raise ValidationError(
                _('Debe tener al menos 2 caracteres.'),
                code='too_short'
            )
        
        # Máximo 50 caracteres
        if len(str(value)) > 50:
            raise ValidationError(
                _('No puede exceder los 50 caracteres.'),
                code='too_long'
            )
        
        return value.title().strip()

class TelefonoValidator:
    """
    Validador de teléfono argentino
    """
    def __call__(self, value):
        if not value:
            return
        
        # Patrones aceptados
        patrones = [
            r'^\d{10}$',  # 3511234567
            r'^\d{8}$',   # 12345678
            r'^\+54 \d{2} \d{8}$',  # +54 351 1234567
            r'^\+54 \d{10}$',  # +54 3511234567
            r'^\(\d{3}\) \d{3}-\d{4}$',  # (351) 123-4567
            r'^\d{2}-\d{8}$',  # 351-1234567
        ]
        
        valor = str(value).strip()
        
        # Verificar si coincide con algún patrón
        if not any(re.match(patron, valor) for patron in patrones):
            raise ValidationError(
                _('Formato de teléfono inválido. Ejemplos válidos: 3511234567, (351) 123-4567, +54 351 1234567'),
                code='invalid_phone'
            )
        
        return valor

class EmailValidator:
    """
    Validador de email con formato específico
    """
    def __call__(self, value):
        if not value:
            return
        
        email = str(value).strip().lower()
        
        # Patrón de email básico
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError(
                _('Formato de email inválido. Debe ser: usuario@dominio.com'),
                code='invalid_email'
            )
        
        # Validar dominio común (opcional)
        dominios_validos = ['.com', '.com.ar', '.ar', '.gob.ar', '.edu.ar', '.org', '.net']
        if not any(email.endswith(dom) for dom in dominios_validos):
            raise ValidationError(
                _('Dominio de email no válido. Use dominios como: .com, .com.ar, .ar, .gob.ar'),
                code='invalid_domain'
            )
        
        return email

class PasswordValidator:
    """
    Validador de contraseña segura
    """
    def __init__(self, min_length=8, require_upper=True, require_lower=True, require_digit=True):
        self.min_length = min_length
        self.require_upper = require_upper
        self.require_lower = require_lower
        self.require_digit = require_digit
    
    def __call__(self, value):
        if not value:
            raise ValidationError(
                _('La contraseña no puede estar vacía.'),
                code='password_empty'
            )
        
        password = str(value)
        errors = []
        
        # Validar longitud mínima
        if len(password) < self.min_length:
            errors.append(f'Mínimo {self.min_length} caracteres')
        
        # Validar mayúscula
        if self.require_upper and not any(c.isupper() for c in password):
            errors.append('Al menos una letra mayúscula')
        
        # Validar minúscula
        if self.require_lower and not any(c.islower() for c in password):
            errors.append('Al menos una letra minúscula')
        
        # Validar número
        if self.require_digit and not any(c.isdigit() for c in password):
            errors.append('Al menos un número')
        
        # Validar caracteres especiales (opcional)
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append('Al menos un carácter especial (!@#$%^&*)')
        
        if errors:
            raise ValidationError(
                _('La contraseña debe contener: %(requirements)s') % {
                    'requirements': ', '.join(errors)
                },
                code='weak_password'
            )
        
        return value

class NumeroOrdenValidator:
    """
    Validador de número de orden único
    """
    def __init__(self, model, field_name='numero_orden'):
        self.model = model
        self.field_name = field_name
    
    def __call__(self, value, instance=None):
        if not value:
            return
        
        # Verificar si ya existe otro registro con el mismo número
        query = self.model.objects.filter(**{self.field_name: value})
        
        # Si estamos editando un registro existente, excluirlo
        if instance and instance.pk:
            query = query.exclude(pk=instance.pk)
        
        if query.exists():
            raise ValidationError(
                _('Ya existe un registro con este número de orden.'),
                code='duplicate_number'
            )
        
        # Validar que sea positivo
        if value <= 0:
            raise ValidationError(
                _('El número de orden debe ser positivo.'),
                code='invalid_number'
            )
        
        return value
    

class ImagenDuplicadaValidator:
    """
    Valida que la imagen subida no sea igual o similar a una ya existente.
    Usar en el método clean_imagen_marca() del form.
    """
    def __init__(self, excluir_id=None):
        self.excluir_id = excluir_id

    def __call__(self, imagen_field):
        from app_registros.image_similarity import (
            calcular_hash, buscar_duplicados_marca,
            buscar_duplicados_predefinida, HASH_THRESHOLD,
        )
        from django.core.exceptions import ValidationError

        hash_nuevo = calcular_hash(imagen_field)
        if not hash_nuevo:
            return

        duplicados_marcas = buscar_duplicados_marca(hash_nuevo, excluir_id=self.excluir_id)
        if duplicados_marcas:
            mejor = duplicados_marcas[0]
            raise ValidationError(
                f'Esta imagen ya está registrada para el productor "{mejor["productor"]}" '
                f'(Marca #{mejor["numero_orden"]}). Usá una imagen diferente.',
                code='imagen_duplicada_marca',
            )

        duplicados_pred = buscar_duplicados_predefinida(hash_nuevo)
        if duplicados_pred:
            mejor = duplicados_pred[0]
            raise ValidationError(
                f'Esta imagen ya existe como imagen predefinida: "{mejor["nombre"]}". '
                f'Seleccionala desde el catálogo de imágenes predefinidas.',
                code='imagen_duplicada_predefinida',
            )


import os
from django.core.exceptions import ValidationError

TAM_MAX_IMAGEN = 5 * 1024 * 1024      # 5 MB
TAM_MAX_DOCUMENTO = 10 * 1024 * 1024  # 10 MB

EXT_IMAGEN = {'.jpg', '.jpeg', '.png', '.webp'}
EXT_DOCUMENTO = {'.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx'}


def _validar_archivo(archivo, extensiones, tam_max, nombre_tipo):
    ext = os.path.splitext(archivo.name)[1].lower()
    if ext not in extensiones:
        permitidas = ', '.join(sorted(extensiones))
        raise ValidationError(f'Formato no permitido. Se aceptan: {permitidas}.')
    if archivo.size > tam_max:
        raise ValidationError(f'El archivo supera el máximo de {tam_max // (1024 * 1024)} MB.')


def validar_imagen_segura(archivo):
    """Imagen: extensión permitida y máximo 5 MB."""
    _validar_archivo(archivo, EXT_IMAGEN, TAM_MAX_IMAGEN, 'imagen')


def validar_documento_seguro(archivo):
    """Documento: extensión permitida, máximo 10 MB y, si es PDF, que realmente lo sea."""
    _validar_archivo(archivo, EXT_DOCUMENTO, TAM_MAX_DOCUMENTO, 'documento')
    if archivo.name.lower().endswith('.pdf'):
        inicio = archivo.read(5)
        archivo.seek(0)
        if inicio != b'%PDF-':
            raise ValidationError('El archivo no es un PDF válido.')



