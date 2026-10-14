from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import Productor, Campo, TipoSenal, MarcaSenal, Solicitud, UserProfile, ChangeLog, ImagenMarcaPredefinida

@admin.register(Productor)
class ProductorAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'dni', 'localidad', 'estado', 'fecha_registro']
    list_filter = ['estado', 'localidad', 'fecha_registro']
    search_fields = ['nombre', 'apellido', 'dni', 'cuit']
    readonly_fields = ['fecha_registro']

@admin.register(Campo)
class CampoAdmin(GISModelAdmin):
    list_display = ['nombre', 'productor', 'distrito', 'departamento', 'area_hectareas']
    list_filter = ['distrito', 'departamento']
    search_fields = ['nombre', 'productor__nombre', 'productor__apellido']
    gis_widget_kwargs = {
        'attrs': {
            'default_lon': -7322596,
            'default_lat': -3346556,
            'default_zoom': 8,
        }
    }

@admin.register(TipoSenal)
class TipoSenalAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ubicacion_oreja']
    list_filter = ['ubicacion_oreja']

@admin.register(MarcaSenal)
class MarcaSenalAdmin(admin.ModelAdmin):
    list_display = ['numero_orden', 'productor', 'tipo_tramite', 'estado', 'fecha_inscripcion']
    list_filter = ['tipo_tramite', 'estado', 'fecha_inscripcion']
    search_fields = ['numero_orden', 'productor__nombre', 'productor__apellido']
    readonly_fields = ['fecha_creacion', 'ultima_modificacion']

@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = ['id', 'productor', 'tipo_tramite', 'estado', 'fecha_solicitud']
    list_filter = ['tipo_tramite', 'estado', 'fecha_solicitud']
    search_fields = ['productor__nombre', 'productor__apellido']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'rol', 'fecha_alta']
    list_filter = ['rol', 'fecha_alta']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']

@admin.register(ChangeLog)
class ChangeLogAdmin(admin.ModelAdmin):
    list_display = ['modelo', 'objeto_id', 'accion', 'user', 'timestamp']
    list_filter = ['modelo', 'accion', 'timestamp']
    search_fields = ['modelo', 'objeto_id', 'user__username']
    readonly_fields = ['timestamp']



@admin.register(ImagenMarcaPredefinida)
class ImagenMarcaPredefinidaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo_marca', 'activa']
    list_filter = ['tipo_marca', 'activa']
    search_fields = ['nombre', 'descripcion']