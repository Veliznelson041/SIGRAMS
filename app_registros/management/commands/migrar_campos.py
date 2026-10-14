from django.core.management.base import BaseCommand
from app_registros.models import Productor, Campo

class Command(BaseCommand):
    help = 'Migra los datos de campo de los productores a objetos Campo'

    def handle(self, *args, **options):
        count = 0
        for productor in Productor.objects.all():
            if not productor.campos.exists():
                # Crear campo automáticamente
                Campo.objects.create(
                    nombre=productor.campo or f"Campo de {productor.nombre} {productor.apellido}",
                    productor=productor,
                    distrito=productor.localidad or "Sin especificar",
                    departamento=productor.departamento or "Sin especificar",
                    area_hectareas=productor.area_hectareas or 0,
                    latitud=productor.latitud,
                    longitud=productor.longitud
                )
                count += 1
                self.stdout.write(f'✓ Campo creado para {productor.nombre_completo}')
        
        self.stdout.write(self.style.SUCCESS(f'\nSe crearon {count} campos automáticamente'))