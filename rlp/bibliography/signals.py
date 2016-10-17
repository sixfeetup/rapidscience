from django.dispatch import receiver

from rlp.accounts.signals import sync_user
from .models import fetch_publications_for_user


@receiver(sync_user, dispatch_uid='fetch_publications')
def update_publications(sender, **kwargs):
    user = kwargs.get('user')
    # Only hit the API if they have an ORCID id and don't yet have any publications listed
    if user.orcid and not user.publication_set.count():
        fetch_publications_for_user(user)
