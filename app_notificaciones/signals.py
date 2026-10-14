from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from app_registros.models import Solicitud, ChangeLog, DocumentoSolicitud
from app_notificaciones.models import Notificacion


@receiver(post_save, sender=Solicitud)
def notificar_cambio_estado_solicitud(sender, instance, created, **kwargs):
    """
    Notifica cambios en el estado de una solicitud
    """
    if not created:  # Solo para actualizaciones
        try:
            # Obtener el estado anterior (puedes usar ChangeLog o comparar con la base de datos)
            estado_anterior = Solicitud.objects.get(pk=instance.pk).estado
            
            if instance.estado != estado_anterior:
                # Notificar al solicitante
                if instance.solicitante and instance.solicitante != instance.revisor:
                    Notificacion.crear_notificacion(
                        usuario=instance.solicitante,
                        titulo=f'Solicitud {instance.get_estado_display()}',
                        mensaje=f'Tu solicitud #{instance.id} ha cambiado a estado: {instance.get_estado_display()}',
                        tipo='info' if instance.estado != 'RECHAZADO' else 'error',
                        contenido_relacionado=instance,
                        url=f'/solicitudes/{instance.id}/'
                    )
                
                # Notificar al revisor (si hay uno y no es el mismo que solicitante)
                if instance.revisor and instance.revisor != instance.solicitante:
                    Notificacion.crear_notificacion(
                        usuario=instance.revisor,
                        titulo=f'Solicitud {instance.get_estado_display()}',
                        mensaje=f'La solicitud #{instance.id} que revisaste ahora está: {instance.get_estado_display()}',
                        tipo='info',
                        contenido_relacionado=instance,
                        url=f'/solicitudes/{instance.id}/'
                    )
                
                # Notificar a administradores cuando una solicitud es aprobada
                if instance.estado == 'APROBADO':
                    administradores = User.objects.filter(
                        userprofile__rol='admin'
                    ).exclude(id=instance.solicitante.id if instance.solicitante else 0)
                    
                    for admin in administradores:
                        Notificacion.crear_notificacion(
                            usuario=admin,
                            titulo='Solicitud Aprobada',
                            mensaje=f'La solicitud #{instance.id} ha sido aprobada por {instance.aprobador.username if instance.aprobador else "un usuario"}',
                            tipo='exito',
                            contenido_relacionado=instance,
                            url=f'/solicitudes/{instance.id}/'
                        )
        
        except Solicitud.DoesNotExist:
            pass


@receiver(post_save, sender=Solicitud)
def notificar_nueva_solicitud(sender, instance, created, **kwargs):
    """
    Notifica la creación de una nueva solicitud
    """
    if created:
        # Notificar a administradores
        administradores = User.objects.filter(
            userprofile__rol__in=['admin', 'empleado']
        )
        
        for admin in administradores:
            if admin != instance.solicitante:  # No notificar al creador
                Notificacion.crear_notificacion(
                    usuario=admin,
                    titulo='Nueva Solicitud Creada',
                    mensaje=f'Nueva solicitud #{instance.id} de tipo: {instance.get_tipo_tramite_display()}',
                    tipo='alerta',
                    contenido_relacionado=instance,
                    url=f'/solicitudes/{instance.id}/'
                )


@receiver(post_save, sender=DocumentoSolicitud)
def notificar_documento_subido(sender, instance, created, **kwargs):
    """
    Notifica cuando se sube un documento a una solicitud
    """
    if created and instance.solicitud:
        # Notificar al revisor (si hay uno) y no es quien subió el documento
        if instance.solicitud.revisor and instance.usuario_subida != instance.solicitud.revisor:
            Notificacion.crear_notificacion(
                usuario=instance.solicitud.revisor,
                titulo='Documento Subido',
                mensaje=f'Se ha subido un documento a la solicitud #{instance.solicitud.id}',
                tipo='info',
                contenido_relacionado=instance.solicitud,
                url=f'/solicitudes/{instance.solicitud.id}/'
            )
        
        # Notificar a otros usuarios relevantes
        usuarios_relacionados = set()
        
        if instance.solicitud.solicitante:
            usuarios_relacionados.add(instance.solicitud.solicitante)
        if instance.solicitud.aprobador:
            usuarios_relacionados.add(instance.solicitud.aprobador)
        
        for usuario in usuarios_relacionados:
            if usuario != instance.usuario_subida:
                Notificacion.crear_notificacion(
                    usuario=usuario,
                    titulo='Documento Subido',
                    mensaje=f'Se ha subido un documento a la solicitud #{instance.solicitud.id}',
                    tipo='info',
                    contenido_relacionado=instance.solicitud,
                    url=f'/solicitudes/{instance.solicitud.id}/'
                )


@receiver(post_save, sender=ChangeLog)
def notificar_log_importante(sender, instance, created, **kwargs):
    """
    Notifica cambios importantes registrados en el log
    """
    if created and instance.modelo == 'Solicitud':
        # Filtrar solo acciones importantes
        if instance.accion in ['APROBADO', 'RECHAZADO', 'OBSERVADO']:
            try:
                from app_registros.models import Solicitud
                solicitud = Solicitud.objects.get(id=instance.objeto_id)
                
                # Notificar al solicitante si hay cambio de estado importante
                if solicitud.solicitante and instance.user != solicitud.solicitante:
                    Notificacion.crear_notificacion(
                        usuario=solicitud.solicitante,
                        titulo=f'Solicitud {instance.accion.capitalize()}',
                        mensaje=f'Tu solicitud #{solicitud.id} ha sido {instance.accion.lower()}',
                        tipo='alerta',
                        contenido_relacionado=solicitud,
                        url=f'/solicitudes/{solicitud.id}/'
                    )
            
            except Solicitud.DoesNotExist:
                pass