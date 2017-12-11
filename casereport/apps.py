from django.apps import AppConfig


class CaseReportConfig(AppConfig):
    name = 'casereport'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('CaseReport'))
        from casereport import signals  # noqa
