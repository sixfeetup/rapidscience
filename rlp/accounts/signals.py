from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver, Signal

from .models import UserLogin


sync_user = Signal(providing_args=['user'])


@receiver(user_logged_in)
def log_login(**kwargs):
    UserLogin.objects.create(user=kwargs['user'])

