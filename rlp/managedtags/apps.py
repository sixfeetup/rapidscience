from django.apps import AppConfig

class ManagedtagsConfig(AppConfig):
    name = 'rlp.managedtags'
    verbose_name = 'ManagedTags'


    def ready(self):
        from . import signals
