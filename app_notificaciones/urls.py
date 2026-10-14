from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_notificaciones, name='lista_notificaciones'),
    path('<int:notificacion_id>/leida/', views.marcar_leida, name='marcar_notificacion_leida'),
    path('marcar-todas-leidas/', views.marcar_todas_leidas, name='marcar_todas_leidas'),
    path('api/no-leidas/', views.obtener_notificaciones_no_leidas, name='api_notificaciones_no_leidas'),
    path('api/contador/', views.contador_notificaciones, name='api_contador_notificaciones'),
]