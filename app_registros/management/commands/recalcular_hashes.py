import os
from django.core.management.base import BaseCommand
from django.conf import settings
from app_registros.image_similarity import calcular_hash_desde_path


class Command(BaseCommand):
    help = 'Recalcula los hashes perceptuales de las imágenes ya cargadas.'

    def handle(self, *args, **options):
        self._procesar_marcas()
        self._procesar_predefinidas()

    def _procesar_marcas(self):
        from app_registros.models import MarcaSenal
        marcas = MarcaSenal.objects.exclude(imagen_marca='').exclude(imagen_marca__isnull=True)
        self.stdout.write(f'Procesando {marcas.count()} marcas...')
        ok = 0
        for marca in marcas:
            path = os.path.join(settings.MEDIA_ROOT, marca.imagen_marca.name)
            if os.path.exists(path):
                hash_val = calcular_hash_desde_path(path)
                if hash_val:
                    marca.image_hash = hash_val
                    marca.save(update_fields=['image_hash'])
                    ok += 1
        self.stdout.write(self.style.SUCCESS(f'MarcaSenal: {ok} procesadas'))

    def _procesar_predefinidas(self):
        from app_registros.models import ImagenMarcaPredefinida
        imgs = ImagenMarcaPredefinida.objects.exclude(imagen='').exclude(imagen__isnull=True)
        self.stdout.write(f'Procesando {imgs.count()} imágenes predefinidas...')
        ok = 0
        for img in imgs:
            path = os.path.join(settings.MEDIA_ROOT, img.imagen.name)
            if os.path.exists(path):
                hash_val = calcular_hash_desde_path(path)
                if hash_val:
                    img.image_hash = hash_val
                    img.save(update_fields=['image_hash'])
                    ok += 1
        self.stdout.write(self.style.SUCCESS(f'ImagenMarcaPredefinida: {ok} procesadas'))