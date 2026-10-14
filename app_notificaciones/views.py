from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import Notificacion
from django.core.paginator import Paginator


@login_required
def lista_notificaciones(request):
    """Lista todas las notificaciones del usuario"""
    notificaciones = Notificacion.objects.filter(usuario=request.user)
    
    # Filtros
    tipo = request.GET.get('tipo', '')
    leida = request.GET.get('leida', '')
    
    if tipo:
        notificaciones = notificaciones.filter(tipo=tipo)
    
    if leida == 'true':
        notificaciones = notificaciones.filter(leida=True)
    elif leida == 'false':
        notificaciones = notificaciones.filter(leida=False)
    
    # Paginación
    paginator = Paginator(notificaciones, 20)
    page = request.GET.get('page')
    notificaciones_pagina = paginator.get_page(page)
    
    # Estadísticas
    total = notificaciones.count()
    no_leidas = notificaciones.filter(leida=False).count()
    
    context = {
        'notificaciones': notificaciones_pagina,
        'total_notificaciones': total,
        'no_leidas': no_leidas,
        'tipos': Notificacion.TIPOS,
        'tipo_filtro': tipo,
        'leida_filtro': leida,
    }
    
    return render(request, 'app_notificaciones/lista.html', context)


@login_required
def marcar_leida(request, notificacion_id):
    """Marca una notificación como leída"""
    notificacion = get_object_or_404(
        Notificacion, 
        id=notificacion_id, 
        usuario=request.user
    )
    
    notificacion.marcar_como_leida()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'leida': notificacion.leida
        })
    
    return redirect('lista_notificaciones')


@login_required
def marcar_todas_leidas(request):
    """Marca todas las notificaciones del usuario como leídas"""
    Notificacion.objects.filter(
        usuario=request.user, 
        leida=False
    ).update(leida=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('lista_notificaciones')


@login_required
def obtener_notificaciones_no_leidas(request):
    """API para obtener notificaciones no leídas (para AJAX)"""
    notificaciones = Notificacion.objects.filter(
        usuario=request.user,
        leida=False
    ).order_by('-fecha_creacion')[:10]
    
    data = []
    for notif in notificaciones:
        data.append({
            'id': notif.id,
            'titulo': notif.titulo,
            'mensaje': notif.mensaje,
            'tipo': notif.tipo,
            'tiempo': notif.tiempo_transcurrido,
            'url': notif.url or '#',
            'es_reciente': notif.es_reciente,
        })
    
    return JsonResponse({
        'notificaciones': data,
        'total': notificaciones.count()
    })


@login_required
def contador_notificaciones(request):
    """API para obtener el contador de notificaciones no leídas"""
    count = Notificacion.objects.filter(
        usuario=request.user,
        leida=False
    ).count()
    
    return JsonResponse({'count': count})