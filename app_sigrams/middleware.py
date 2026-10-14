from django.shortcuts import redirect
from django.urls import reverse


class RestringirInspectorMiddleware:
    """
    Los usuarios con rol 'inspector' solo pueden acceder a su pantalla
    de búsqueda dedicada (y login/logout/estáticos). Cualquier otra URL
    los redirige de vuelta, sin importar que la escriban a mano.
    """
    RUTAS_PERMITIDAS_PREFIJOS = (
        '/inspector/',
        '/logout/',
        '/notificaciones/api/',
        '/static/',
        '/media/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)

        if user and user.is_authenticated:
            try:
                es_inspector = user.userprofile.rol == 'inspector'
            except Exception:
                es_inspector = False

            if es_inspector:
                path = request.path
                permitido = any(path.startswith(p) for p in self.RUTAS_PERMITIDAS_PREFIJOS)
                if not permitido:
                    return redirect('busqueda_inspector')

        return self.get_response(request)