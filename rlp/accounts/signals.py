from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver, Signal
from django.template.loader import render_to_string

from .models import UserLogin

from actstream.models import Action

sync_user = Signal(providing_args=['user'])

@receiver(user_logged_in)
def log_login(**kwargs):
    UserLogin.objects.create(user=kwargs['user'])
    if UserLogin.objects.filter(user=kwargs['user']).count() == 1:
        # on the user's first login, welcome them
        #success()
        tips_text = render_to_string("accounts/new_member_tips.html", {})
        tips = Action.objects.create(actor=kwargs['user'],
                              verb='joined',
                              action_object=kwargs['user'],
                              description=tips_text,
                              )
        tips.save()

