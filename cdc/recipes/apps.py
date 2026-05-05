"""App configuration for the recipes module."""

from django.apps import AppConfig


class RecipesConfig(AppConfig):
    """Configures the recipes Django app, including app name and verbose name."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cdc.recipes'
