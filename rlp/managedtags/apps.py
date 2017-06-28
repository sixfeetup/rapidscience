from django.apps import AppConfig


class ManagedtagsConfig(AppConfig):
    name = 'rlp.managedtags'


   def ready(self):
        from . import signals
