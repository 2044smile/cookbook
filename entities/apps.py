from cookbook.settings import DEFAULT_AUTO_FIELD
from django.apps import AppConfig


class EntitiesConfig(AppConfig):
    DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
    name = 'entities'
