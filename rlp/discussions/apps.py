from django.apps import AppConfig


class DiscussionsConfig(AppConfig):
    name = 'rlp.discussions'
    verbose_name = "Discussions"

    def ready(self):
        from . import signals
        from actstream import registry
        registry.register(self.get_model('ThreadedComment'))
