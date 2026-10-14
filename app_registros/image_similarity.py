"""
image_similarity.py
-------------------
Detecta imágenes duplicadas o similares usando hashing perceptual (pHash).
No requiere API externa: todo se procesa localmente.
"""

import imagehash
from PIL import Image
import io

# Umbral de distancia de Hamming (0=idénticas, >8=muy diferentes)
HASH_THRESHOLD = 3 #lo cambie a 5 para que sea más estricto, antes estaba en 8
HASH_SIZE = 16


def calcular_hash(imagen_field):
    """Recibe un ImageField de Django y devuelve su hash perceptual."""
    if not imagen_field:
        return None
    try:
        imagen_field.seek(0)
        img_bytes = imagen_field.read()
        imagen_field.seek(0)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        return str(imagehash.phash(img, hash_size=HASH_SIZE))
    except Exception:
        return None


def calcular_hash_desde_path(path):
    """Calcula el hash desde una ruta de archivo en disco."""
    try:
        img = Image.open(path).convert("RGB")
        return str(imagehash.phash(img, hash_size=HASH_SIZE))
    except Exception:
        return None


def calcular_hash_desde_bytes(img_bytes):
    """Calcula el hash desde bytes crudos. Usado en las vistas AJAX."""
    try:
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        return str(imagehash.phash(img, hash_size=HASH_SIZE))
    except Exception:
        return None


def distancia(hash_a: str, hash_b: str) -> int:
    try:
        return imagehash.hex_to_hash(hash_a) - imagehash.hex_to_hash(hash_b)
    except Exception:
        return 999


def son_similares(hash_a: str, hash_b: str, threshold: int = HASH_THRESHOLD) -> bool:
    if not hash_a or not hash_b:
        return False
    return distancia(hash_a, hash_b) <= threshold


def buscar_duplicados_marca(hash_nuevo: str, excluir_id: int = None) -> list:
    """Busca en MarcaSenal imágenes visualmente similares."""
    from app_registros.models import MarcaSenal
    if not hash_nuevo:
        return []
    qs = MarcaSenal.objects.exclude(image_hash__isnull=True).exclude(image_hash="")
    if excluir_id:
        qs = qs.exclude(pk=excluir_id)
    duplicados = []
    for marca in qs.select_related("productor"):
        if son_similares(hash_nuevo, marca.image_hash):
            duplicados.append({
                "id": marca.pk,
                "numero_orden": marca.numero_orden,
                "productor": str(marca.productor),
                "productor_id": marca.productor.pk,
                "descripcion": marca.descripcion_marca[:80],
                "distancia": distancia(hash_nuevo, marca.image_hash),
                "imagen_url": marca.imagen_marca.url if marca.imagen_marca else None,
            })
    duplicados.sort(key=lambda x: x["distancia"])
    return duplicados


def buscar_duplicados_predefinida(hash_nuevo: str, excluir_id: int = None) -> list:
    """Busca en ImagenMarcaPredefinida imágenes visualmente similares."""
    from app_registros.models import ImagenMarcaPredefinida
    if not hash_nuevo:
        return []
    qs = ImagenMarcaPredefinida.objects.exclude(image_hash__isnull=True).exclude(image_hash="")
    if excluir_id:
        qs = qs.exclude(pk=excluir_id)
    duplicados = []
    for img in qs:
        if son_similares(hash_nuevo, img.image_hash):
            duplicados.append({
                "id": img.pk,
                "nombre": img.nombre,
                "tipo_marca": img.get_tipo_marca_display(),
                "distancia": distancia(hash_nuevo, img.image_hash),
            })
    duplicados.sort(key=lambda x: x["distancia"])
    return duplicados


def buscar_en_todo(hash_nuevo: str, excluir_marca_id: int = None) -> dict:
    """Busca duplicados en ambas tablas a la vez."""
    return {
        "marcas": buscar_duplicados_marca(hash_nuevo, excluir_id=excluir_marca_id),
        "predefinidas": buscar_duplicados_predefinida(hash_nuevo),
    }