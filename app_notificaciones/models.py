from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone


class Notificacion(models.Model):
    """Modelo para notificaciones internas del sistema"""
    
    TIPOS = (
        ('info', 'Informativa'),
        ('alerta', 'Alerta'),
        ('urgente', 'Urgente'),
        ('exito', 'Éxito'),
        ('error', 'Error'),
    )
    
    # Usuario destinatario
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notificaciones'
    )
    
    # Contenido de la notificación
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS, default='info')
    
    # Estado
    leida = models.BooleanField(default=False)
    
    # Relación genérica con cualquier modelo
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    contenido_relacionado = GenericForeignKey('content_type', 'object_id')
    
    # URL a la que redirigir (opcional)
    url = models.CharField(max_length=500, blank=True, null=True)
    
    # Fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_leida = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        indexes = [
            models.Index(fields=['usuario', 'leida', 'fecha_creacion']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"
    
    def marcar_como_leida(self):
        """Marca la notificación como leída"""
        if not self.leida:
            self.leida = True
            self.fecha_leida = timezone.now()
            self.save()
    
    @property
    def es_reciente(self):
        """Indica si la notificación es reciente (menos de 24 horas)"""
        return (timezone.now() - self.fecha_creacion).seconds < 86400
    
    @property
    def tiempo_transcurrido(self):
        """Devuelve el tiempo transcurrido en formato legible"""
        delta = timezone.now() - self.fecha_creacion
        
        if delta.days > 0:
            return f"Hace {delta.days} día{'s' if delta.days > 1 else ''}"
        elif delta.seconds > 3600:
            horas = delta.seconds // 3600
            return f"Hace {horas} hora{'s' if horas > 1 else ''}"
        elif delta.seconds > 60:
            minutos = delta.seconds // 60
            return f"Hace {minutos} minuto{'s' if minutos > 1 else ''}"
        else:
            return "Ahora mismo"
    
    @classmethod
    def crear_notificacion(cls, usuario, titulo, mensaje, tipo='info', 
                          contenido_relacionado=None, url=None):
        """Método helper para crear notificaciones"""
        notificacion = cls.objects.create(
            usuario=usuario,
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo,
            contenido_relacionado=contenido_relacionado,
            url=url
        )
        return notificacion