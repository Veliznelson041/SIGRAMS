from django.apps import AppConfig


class AppNotificacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_notificaciones'
    
    def ready(self):
        # Importar las señales
        import app_notificaciones.signals