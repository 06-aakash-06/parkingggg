from django.apps import AppConfig

class ParkingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'parking'
    
    def ready(self):
        # Import your views AFTER apps are loaded
        from . import views