from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, FileExtensionValidator

from .validators import validar_imagen_segura, validar_documento_seguro

# ----------------------------------------
# PRODUCTOR GANADERO (Modelo principal)
# ----------------------------------------
class Productor(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('REGISTRADO', 'Registrado'),
        ('RENOVACION', 'Renovación'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('BAJA', 'Baja'),
    ]
    
    nombre = models.CharField(max_length=150)
    apellido = models.CharField(max_length=150)
    dni = models.CharField(max_length=15, unique=True, verbose_name="DNI")
    cuit = models.CharField(max_length=20, blank=True, null=True, verbose_name="CUIT")
    
    # Campos de dirección mejorados
    calle = models.CharField(max_length=300, blank=True, null=True)  # Cambiado de domicilio a calle
    campo = models.CharField(max_length=200, blank=True, null=True)
    localidad = models.CharField(max_length=150, blank=True, null=True)
    municipio = models.CharField(max_length=150, blank=True, null=True)
    departamento = models.CharField(max_length=150, blank=True, null=True)
    provincia = models.CharField(max_length=150, default="Catamarca")
    
    telefono = models.CharField(max_length=80, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    # Georreferenciación
    latitud = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitud = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    area_hectareas = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Productor"
        verbose_name_plural = "Productores"
        ordering = ['apellido', 'nombre']
    
    def __str__(self):
        return f"{self.apellido}, {self.nombre} ({self.dni})"
    
    @property
    def nombre_completo(self):
        return f"{self.apellido}, {self.nombre}"
    
    @property
    def direccion_completa(self):
        parts = []
        if self.calle:
            parts.append(self.calle)
        if self.localidad:
            parts.append(self.localidad)
        if self.municipio:
            parts.append(self.municipio)
        if self.departamento:
            parts.append(self.departamento)
        if self.provincia:
            parts.append(self.provincia)
        return ", ".join(parts)

# ----------------------------------------
# CAMPO
# ----------------------------------------
class Campo(models.Model):
    nombre = models.CharField(max_length=200)
    productor = models.ForeignKey(Productor, on_delete=models.CASCADE, related_name='campos')
    area_hectareas = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    distrito = models.CharField(max_length=150)
    departamento = models.CharField(max_length=150)
    latitud = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitud = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    poligono = gis_models.PolygonField(srid=4326, blank=True, null=True)
    observaciones = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.distrito}"

# ----------------------------------------
# TIPO DE SEÑAL (usando "Senal" sin ñ para evitar problemas)
# ----------------------------------------
class TipoSenal(models.Model):
    UBICACION_OREJA_CHOICES = [
        ('DERECHA', 'Oreja derecha'),
        ('IZQUIERDA', 'Oreja izquierda'),
        ('AMBAS', 'Ambas orejas'),
    ]
    
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    ubicacion_oreja = models.CharField(max_length=20, choices=UBICACION_OREJA_CHOICES)
    imagen_referencia = models.ImageField(upload_to='referencias/', blank=True, null=True, validators=[validar_imagen_segura])

    def __str__(self):
        return self.nombre

# ----------------------------------------
# MARCA Y SEÑAL (Modelo principal para registros)
# ----------------------------------------


class ImagenMarcaPredefinida(models.Model):
    TIPO_MARCA_CHOICES = [
        ('FLANCO', 'Flanco'),
        ('ANCA', 'Anca'),
        ('COSTILLAR', 'Costillar'),
        ('PALETA', 'Paleta'),
        ('CUELLO', 'Cuello'),
        ('MEJILLA', 'Mejilla'),
        ('OTRO', 'Otro'),
    ]
    
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='marcas/predefinidas/', validators=[validar_imagen_segura])
    tipo_marca = models.CharField(max_length=20, choices=TIPO_MARCA_CHOICES, default='FLANCO')
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)
    image_hash = models.CharField(
        max_length=128, blank=True, null=True,
        verbose_name='Hash perceptual', db_index=True,
    )

    def save(self, *args, **kwargs):
        if self.imagen:
            try:
                from app_registros.image_similarity import calcular_hash
                nuevo_hash = calcular_hash(self.imagen)
                if nuevo_hash:
                    self.image_hash = nuevo_hash
            except Exception:
                pass
        super().save(*args, **kwargs)


    class Meta:
        verbose_name = "Imagen de Marca Predefinida"
        verbose_name_plural = "Imágenes de Marcas Predefinidas"
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_marca_display()})"



from django.db import models
from django.db.models import Max
from django.utils import timezone
from django.core.validators import MinValueValidator


class MarcaSenal(models.Model):

    TIPO_TRAMITE_CHOICES = [
        ('REGISTRO_MARCA_SENAL', 'Registro Marca y Señal'),
        ('REGISTRO_SENALES', 'Registro Señales solas'),
    ]

    ESTADO_CHOICES = [
        ('VIGENTE', 'Vigente'),
        ('VENCIDA', 'Vencida'),
        ('BAJA', 'Baja'),
        ('EN_TRAMITE', 'En trámite'),
    ]

    # ============================
    # DATOS BÁSICOS
    # ============================
    productor = models.ForeignKey(
        Productor,
        on_delete=models.CASCADE,
        related_name='marcas_senales'
    )

    campo = models.ForeignKey(
        Campo,
        on_delete=models.CASCADE,
        related_name='marcas_senales'
    )

    tipo_tramite = models.CharField(
        max_length=20,
        choices=TIPO_TRAMITE_CHOICES,
        default='NUEVA'
    )

    # ============================
    # INFORMACIÓN DE REGISTRO
    # ============================
    numero_orden = models.PositiveIntegerField(
        unique=True,
        verbose_name="Número de orden",
        editable=False  # 🔥 No aparece en formularios
    )

    fecha_inscripcion = models.DateField(default=timezone.now)
    fecha_vencimiento = models.DateField(blank=True, null=True)

    # ============================
    # MARCAS Y SEÑALES
    # ============================
    descripcion_marca = models.TextField(verbose_name="Descripción de la marca")
    imagen_marca = models.ImageField(upload_to='marcas/', blank=True, null=True, validators=[validar_imagen_segura])

    tipo_senal = models.ForeignKey(
        TipoSenal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    TIPO_MARCA_OPCIONES = [
        ('DIBUJO', 'Dibujo'),
        ('INICIALES', 'Iniciales'),
        ('NUMEROS', 'Números'),
        ('LETRA_NUMERO', 'Letra y Número'),
    ]
    tipo_marca = models.CharField(
        max_length=20,
        choices=TIPO_MARCA_OPCIONES,
        blank=True,
        verbose_name='Tipo de Marca',
    )

    descripcion_senal = models.TextField(
        blank=True,
        verbose_name="Descripción de la señal"
    )

    senales_orejeras = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Señales Orejeras',
    )

    imagenes_predefinidas = models.ManyToManyField(
        ImagenMarcaPredefinida,
        blank=True,
        verbose_name="Imágenes predefinidas",
        help_text="Seleccione una o más imágenes que componen la marca"
    )

    # ============================
    # GANADO
    # ============================
    vacuno = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    caballar = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    mular = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    asnal = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    ovino = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    cabrio = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    porcino = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    camelidos = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])

    # ============================
    # ADMINISTRATIVO
    # ============================
    valor_sellado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='EN_TRAMITE'
    )

    observaciones = models.TextField(blank=True)
    image_hash = models.CharField(
        max_length=128, blank=True, null=True,
        verbose_name='Hash perceptual de imagen_marca', db_index=True,
    )



    # ============================
    # CARNET
    # ============================
    imagen_carnet_frente = models.ImageField(upload_to='carnets/', blank=True, null=True, validators=[validar_imagen_segura])
    imagen_carnet_dorso = models.ImageField(upload_to='carnets/', blank=True, null=True, validators=[validar_imagen_segura])

    # ============================
    # CARNET FÍSICO
    # ============================
    carnet_generado = models.BooleanField(default=False)
    fecha_generacion_carnet = models.DateTimeField(blank=True, null=True)
    carnet_generado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='carnets_generados')

    # ============================
    # AUDITORÍA
    # ============================
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_modificacion = models.DateTimeField(auto_now=True)

    # ============================
    # META
    # ============================
    class Meta:
        verbose_name = "Marca y Señal"
        verbose_name_plural = "Marcas y Señales"
        ordering = ['-fecha_inscripcion']

    # ============================
    # MÉTODOS
    # ============================
    def __str__(self):
        return f"Marca #{self.numero_orden} - {self.productor}"

    @property
    def total_ganado(self):
        return sum([
            self.vacuno,
            self.caballar,
            self.mular,
            self.asnal,
            self.ovino,
            self.cabrio,
            self.porcino,
            self.camelidos,
        ])

    def save(self, *args, **kwargs):
        # Generar número de orden automático
        if not self.numero_orden:
            from django.db.models import Max
            ultimo = MarcaSenal.objects.aggregate(
                Max('numero_orden')
            )['numero_orden__max']
            self.numero_orden = (ultimo or 0) + 1

        # Calcular hash perceptual si hay imagen de marca
        if self.imagen_marca:
            try:
                from app_registros.image_similarity import calcular_hash
                nuevo_hash = calcular_hash(self.imagen_marca)
                if nuevo_hash:
                    self.image_hash = nuevo_hash
            except Exception:
                pass

        super().save(*args, **kwargs)    


# ----------------------------------------
# SOLICITUD////////////////////////////
# ----------------------------------------
from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User
from django.utils import timezone


class Solicitud(models.Model):

    # ----------------------------------------
    # ENUMS
    # ----------------------------------------
    TIPO_TRAMITE_CHOICES = [
        ('RENOVACION', 'Renovación'),
        ('RENOVACION_TRANSFERENCIA', 'Renovación y Transferencia'),
        ('RENOVACION_MOD_SENALES', 'Renovación y Modificación de Señales'),
        ('TRANSFERENCIA_MOD_SENAL', 'Transferencia y Modificación de Señal'),
        ('DUPLICADO', 'Duplicado'),
        ('BAJA', 'Baja'),
        ('REGISTRO_MARCAS_SENALES', 'Registro Marcas y Señales'),
        ('REGISTRO_SENALES', 'Registro Señales'),
    ]

    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_REVISION', 'En revisión'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
        ('OBSERVADO', 'Observado'),
    ]

    PRIORIDAD_CHOICES = [
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente'),
    ]

    TIPO_GANADO_CHOICES = [
        ('VACUNO', 'Vacuno'),
        ('EQUINO', 'Equino'),
        ('MULAR', 'Mular'),
        ('ASNAL', 'Asnal'),
        ('OVINO', 'Ovino'),
        ('CAPRINO', 'Caprino'),
        ('PORCINO', 'Porcino'),
        ('CAMELIDOS', 'Camélidos'),
    ]

    # ----------------------------------------
    # IDENTIFICACIÓN
    # ----------------------------------------
    numero_expediente = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Número de Expediente"
    )

    # ----------------------------------------
    # DATOS PRINCIPALES
    # ----------------------------------------
    productor = models.ForeignKey(
        'Productor',
        on_delete=models.CASCADE,
        related_name='solicitudes'
    )

    tipo_tramite = models.CharField(
        max_length=30,
        choices=TIPO_TRAMITE_CHOICES
    )

    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE'
    )

    prioridad = models.CharField(
        max_length=20,
        choices=PRIORIDAD_CHOICES,
        default='MEDIA'
    )

    # ----------------------------------------
    # GANADO
    # ----------------------------------------
    tipo_ganado = models.CharField(
        max_length=20,
        choices=TIPO_GANADO_CHOICES,
        default='VACUNO'
    )

    cantidad_animales = models.PositiveIntegerField(
        default=0
    )

    # ----------------------------------------
    # SOLICITANTE (cuando no es User)
    # ----------------------------------------
    solicitante_nombre = models.CharField(
        max_length=200,
        blank=True
    )

    solicitante_dni = models.CharField(
        max_length=15,
        blank=True
    )

    # ----------------------------------------
    # DOCUMENTACIÓN
    # ----------------------------------------
    documento_adjunto = models.FileField(
        upload_to='solicitudes/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx']
            ),
            validar_documento_seguro,
        ]
    )

    imagen_adicional_1 = models.ImageField(
        upload_to='solicitudes/imagenes/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[validar_imagen_segura]
    )

    imagen_adicional_2 = models.ImageField(
        upload_to='solicitudes/imagenes/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[validar_imagen_segura]
    )

    documentos_requeridos = models.JSONField(
        default=list,
        blank=True
    )

    documentos_presentados = models.JSONField(
        default=list,
        blank=True
    )

    # ----------------------------------------
    # FECHAS DE GESTIÓN
    # ----------------------------------------
    fecha_recepcion = models.DateField(
        blank=True,
        null=True
    )

    fecha_asignacion = models.DateField(
        blank=True,
        null=True
    )

    fecha_revision = models.DateTimeField(
        blank=True,
        null=True
    )

    fecha_resolucion = models.DateTimeField(
        blank=True,
        null=True
    )

    fecha_vencimiento = models.DateTimeField(
        blank=True,
        null=True
    )

    # ----------------------------------------
    # OBSERVACIONES
    # ----------------------------------------
    motivo = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)
    observaciones_internas = models.TextField(blank=True)

    observaciones_revision = models.TextField(blank=True)
    observaciones_aprobacion = models.TextField(blank=True)

    # ----------------------------------------
    # RELACIONES
    # ----------------------------------------
    marca_senal = models.ForeignKey(
        'MarcaSenal',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='solicitudes'
    )

    productor_destino = models.ForeignKey(
        'Productor',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='solicitudes_recibidas',
        verbose_name='Productor destino (transferencia)'
    )

        # ----------------------------------------
    # MODIFICACIÓN PROPUESTA (solo para RENOVACION_MOD_SENALES / TRANSFERENCIA_MOD_SENAL)
    # ----------------------------------------
    descripcion_marca_nueva = models.TextField(blank=True, verbose_name="Nueva descripción de marca")
    descripcion_senal_nueva = models.TextField(blank=True, verbose_name="Nueva descripción de señal")
    tipo_marca_nueva = models.CharField(
        max_length=20,
        choices=[
            ('DIBUJO', 'Dibujo'),
            ('INICIALES', 'Iniciales'),
            ('NUMEROS', 'Números'),
            ('LETRA_NUMERO', 'Letra y Número'),
        ],
        blank=True,
        verbose_name='Nuevo tipo de marca',
    )
    senales_orejeras_nuevas = models.JSONField(blank=True, null=True, verbose_name='Nuevas señales orejeras')

    solicitante = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='solicitudes_realizadas'
    )

    revisor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_revisadas'
    )

    aprobador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_aprobadas'
    )

    # ----------------------------------------
    # META
    # ----------------------------------------
    class Meta:
        ordering = ['-fecha_solicitud']
        permissions = [
            ('can_review_solicitud', 'Puede revisar solicitudes'),
            ('can_approve_solicitud', 'Puede aprobar solicitudes'),
            ('can_reject_solicitud', 'Puede rechazar solicitudes'),
        ]

    # ----------------------------------------
    # MÉTODOS
    # ----------------------------------------
    def __str__(self):
        return f"Solicitud #{self.id} - {self.get_tipo_tramite_display()}"

    def generar_numero_expediente(self):
        if not self.numero_expediente:
            año = timezone.now().year
            consecutivo = Solicitud.objects.filter(
                fecha_solicitud__year=año
            ).count() + 1
            self.numero_expediente = f"EX-{año}-{consecutivo:05d}"

    def save(self, *args, **kwargs):
        if not self.numero_expediente:
            self.generar_numero_expediente()

        if not self.pk and not self.fecha_recepcion:
            self.fecha_recepcion = timezone.now().date()

        super().save(*args, **kwargs)

    @property
    def tiempo_transcurrido(self):
        if self.fecha_resolucion:
            return self.fecha_resolucion - self.fecha_solicitud
        return timezone.now() - self.fecha_solicitud

    @property
    def dias_pendientes(self):
        return (timezone.now() - self.fecha_solicitud).days

    def esta_vencida(self):
        if self.fecha_vencimiento and self.estado in ['PENDIENTE', 'EN_REVISION']:
            return timezone.now() > self.fecha_vencimiento
        return False


# ----------------------------------------
# PERFIL DE USUARIO
# ----------------------------------------
class UserProfile(models.Model):
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('empleado', 'Empleado'),
        ('inspector', 'Inspector'),
    ]

    ESTADO_CUENTA_CHOICES = [
        ('PENDIENTE', 'Pendiente de aprobación'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='empleado')
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_alta = models.DateTimeField(auto_now_add=True)

    # Flujo de aprobación de cuenta
    estado_cuenta = models.CharField(max_length=20, choices=ESTADO_CUENTA_CHOICES, default='PENDIENTE')
    codigo_activacion = models.CharField(max_length=20, blank=True, null=True)
    aprobado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='cuentas_aprobadas'
    )
    fecha_aprobacion = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.get_rol_display()})"
    
    @property
    def es_administrador(self):
        return self.rol == 'admin'
    

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def crear_user_profile(sender, instance, created, **kwargs):
    """Crea un UserProfile automáticamente al crear un User"""
    if created:
        UserProfile.objects.create(user=instance, rol='empleado')

# ----------------------------------------
# LOG DE CAMBIOS
# ----------------------------------------
class ChangeLog(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    modelo = models.CharField(max_length=120)
    objeto_id = models.CharField(max_length=120)
    accion = models.CharField(max_length=40)
    timestamp = models.DateTimeField(auto_now_add=True)
    snapshot = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.modelo}:{self.objeto_id} {self.accion} @ {self.timestamp}"
    


# app_registros/models.py - AÑADIR ESTO:

class FlujoTramite(models.Model):
    """Workflow configurable para trámites"""
    TIPO_TRAMITE_CHOICES = [
        ('NUEVA_MARCA', 'Nueva Marca'),
        ('RENOVACION', 'Renovación'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('BAJA', 'Baja'),
        ('MODIFICACION', 'Modificación'),
        ('DUPLICADO', 'Duplicado de Carnet'),
    ]
    
    tipo_tramite = models.CharField(max_length=20, choices=TIPO_TRAMITE_CHOICES)
    estado_origen = models.CharField(max_length=50)
    estado_destino = models.CharField(max_length=50)
    rol_requerido = models.CharField(max_length=20, choices=[
        ('SOLICITANTE', 'Solicitante'),
        ('EMPLEADO', 'Empleado'),
        ('ADMIN', 'Administrador'),
        ('INSPECTOR', 'Inspector'),
    ])
    condiciones = models.JSONField(default=dict, blank=True)
    orden = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['tipo_tramite', 'orden']
        unique_together = ['tipo_tramite', 'estado_origen', 'estado_destino']
    
    def __str__(self):
        return f"{self.get_tipo_tramite_display()}: {self.estado_origen} → {self.estado_destino}"

class DocumentoSolicitud(models.Model):
    """Documentos adjuntos a solicitudes"""

    TIPO_DOCUMENTO_CHOICES = [
        ('DNI', 'Documento Nacional de Identidad'),
        ('CUIT', 'Constancia de CUIT'),
        ('DOMICILIO', 'Constancia de Domicilio'),
        ('TITULO', 'Título de Propiedad'),
        ('CONTRATO', 'Contrato de Arrendamiento'),
        ('PLANO', 'Plano del Campo'),
        ('FOTOGRAFIA', 'Fotografía de la Marca'),
        ('OTRO', 'Otro Documento'),
    ]

    solicitud = models.ForeignKey(
        'Solicitud',
        on_delete=models.CASCADE,
        related_name='documentos'
    )

    # Se mantiene nombre (ya lo usabas)
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre del Documento"
    )

    # Unificamos "tipo" → "tipo_documento" (más claro y escalable)
    tipo_documento = models.CharField(
        max_length=50,
        choices=TIPO_DOCUMENTO_CHOICES,
        verbose_name="Tipo de Documento"
    )

    archivo = models.FileField(
        upload_to='solicitudes/documentos/%Y/%m/%d/',
        verbose_name="Archivo",
        validators=[validar_documento_seguro]
    )

    fecha_subida = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Subida"
    )

    usuario_subida = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Usuario que Subió"
    )

    # Nuevo campo agregado (no rompe nada)
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )

    class Meta:
        verbose_name = "Documento de Solicitud"
        verbose_name_plural = "Documentos de Solicitud"
        ordering = ['-fecha_subida']

    def __str__(self):
        # Seguro incluso si no hay expediente aún
        expediente = getattr(self.solicitud, 'numero_expediente', f'Solicitud #{self.solicitud.id}')
        return f"{self.get_tipo_documento_display()} - {expediente}"

    # ===== Métodos útiles =====
    def extension(self):
        import os
        return os.path.splitext(self.archivo.name)[1].lower()

    def es_imagen(self):
        return self.extension() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

