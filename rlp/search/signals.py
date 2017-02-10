
import copy

from django.contrib.contenttypes.models import ContentType
from django.db import models
from haystack.exceptions import NotHandled
from haystack.signals import BaseSignalProcessor
from aldryn_search.signals import add_to_index, remove_from_index

TYPES_TO_INDEX = [
    'cms.title',
    'accounts.User',
    'bibliography.ProjectReference',
    'discussions.ThreadedComment',
    'documents.File',
    'documents.Link',
    'documents.Image',
    'documents.Video'
]

class RLPSignalProcessor(BaseSignalProcessor):

    def setup(self):
        for ct in TYPES_TO_INDEX:
            models.signals.post_save.connect(self.handle_save, sender=ct)
            models.signals.post_delete.connect(self.handle_delete, sender=ct)
        add_to_index.connect(self.handle_save)
        remove_from_index.connect(self.handle_delete)

    def teardown(self):
        for ct in TYPES_TO_INDEX:
            models.signals.post_save.disconnect(self.handle_save, sender=ct)
            models.signals.post_delete.disconnect(self.handle_delete, sender=ct)
        add_to_index.disconnect(self.handle_save)
        remove_from_index.disconnect(self.handle_delete)

    def handle_save(self, sender, instance, **kwargs):
        kwargs = copy.copy(kwargs)

        # Exact copy of Haystack's handle_save()
        # except that we pass any kwargs to the update_object method
        using_backends = self.connection_router.for_write(instance=instance)

        for using in using_backends:
            kwargs['using'] = using

            try:
                index = self.connections[using].get_unified_index().get_index(sender)
                # TODO: This should be done by haystack.
                index.update_object(instance, **kwargs)
            except NotHandled:
                # TODO: Maybe log it or let the exception bubble?
                pass
