from django.apps import AppConfig


class DocumentsConfig(AppConfig):
    name = 'rlp.documents'
    verbose_name = "Documents"

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('File'))
        registry.register(self.get_model('Image'))
        registry.register(self.get_model('Link'))
        registry.register(self.get_model('Video'))

