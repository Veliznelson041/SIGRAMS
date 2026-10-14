# app_registros/management/commands/cargar_datos_iniciales.py
from django.core.management.base import BaseCommand
from app_registros.models import TipoSenal

class Command(BaseCommand):
    help = 'Carga datos iniciales para el sistema'
    
    def handle(self, *args, **kwargs):
        # Crear tipos de señales si no existen
        tipos_senal = [
            {'nombre': 'Corte en V', 'ubicacion_oreja': 'IZQUIERDA', 'descripcion': 'Corte en forma de V en la oreja'},
            {'nombre': 'Corte redondo', 'ubicacion_oreja': 'DERECHA', 'descripcion': 'Corte circular en la oreja'},
            {'nombre': 'Muesca triangular', 'ubicacion_oreja': 'IZQUIERDA', 'descripcion': 'Muesca en forma de triángulo'},
            {'nombre': 'Perforación circular', 'ubicacion_oreja': 'DERECHA', 'descripcion': 'Perforación circular'},
            {'nombre': 'Doble corte', 'ubicacion_oreja': 'AMBAS', 'descripcion': 'Dos cortes paralelos'},
            {'nombre': 'Marca de fuego', 'ubicacion_oreja': 'OTRO', 'descripcion': 'Marca con hierro caliente'},
        ]
        
        for tipo in tipos_senal:
            obj, created = TipoSenal.objects.get_or_create(
                nombre=tipo['nombre'],
                defaults={
                    'ubicacion_oreja': tipo['ubicacion_oreja'],
                    'descripcion': tipo['descripcion']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Tipo de señal creado: {tipo["nombre"]}'))
            else:
                self.stdout.write(self.style.WARNING(f'Tipo de señal ya existe: {tipo["nombre"]}'))
        
        self.stdout.write(self.style.SUCCESS('✅ Datos iniciales cargados correctamente'))