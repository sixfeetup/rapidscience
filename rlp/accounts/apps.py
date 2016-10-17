from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'rlp.accounts'
    verbose_name = "Accounts"

    def ready(self):
        from . import signals
        from actstream import registry
        registry.register(self.get_model('User'))

