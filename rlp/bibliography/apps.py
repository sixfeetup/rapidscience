from django.apps import AppConfig


class BibliographyConfig(AppConfig):
    name = 'rlp.bibliography'
    verbose_name = "Bibliography"

    def ready(self):
        from . import signals
        from actstream import registry
        registry.register(self.get_model('Reference'))
        registry.register(self.get_model('ReferenceShare'))

