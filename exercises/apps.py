from django.apps import AppConfig
    """
    Configuration class for the Exercises application.

    This class sets up the configuration for the 'exercises' app, including
    the default auto field type.
    """

class ExercisesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'exercises'
