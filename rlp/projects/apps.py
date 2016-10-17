from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    name = 'rlp.projects'
    verbose_name = "Projects"

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Project'))

