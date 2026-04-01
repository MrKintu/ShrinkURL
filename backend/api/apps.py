from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        # Initialize Zookeeper range manager on startup
        from .utils.range_manager import range_manager
        range_manager.initialize()
