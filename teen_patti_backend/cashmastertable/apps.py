from django.apps import AppConfig


class GametableConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gametable'

class CashmastertableConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cashmastertable'
