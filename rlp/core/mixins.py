from actstream.models import Action

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from django.db.models import Q

from .models import SharedContent


class SharesContentMixin(Model):
    class Meta:
        abstract = True

    _shared = GenericRelation(
        SharedContent,
        content_type_field='viewer_type',
        object_id_field='viewer_id',
    )

    def bookmark(self, content):
        target = content
        if (hasattr(content, 'polymorphic_model_marker')
           and len(content._meta.parents)):
            # for polymorphic types, bookmark the parent reference
            parent_type = list(content._meta.parents)[-1]
            target = parent_type.objects.non_polymorphic().get(id=content.id)
        SharedContent.objects.create(viewer=self, target=target)

    def remove_bookmark(self, content):
        target = content
        if (hasattr(content, 'polymorphic_model_marker')
           and len(content._meta.parents)):
            # for polymorphic types, bookmark the parent reference
            parent_type = list(content._meta.parents)[-1]
            target = parent_type.objects.non_polymorphic().get(id=content.id)
        viewer_type = ContentType.objects.get_for_model(self)
        target_type = ContentType.objects.get_for_model(target)
        SharedContent.objects.filter(
            target_id=target.id,
            viewer_id=self.id,
            target_type_id=target_type.id,
            viewer_type_id=viewer_type.id,
        ).delete()

    def get_bookmarked_content(self, type_class=None):
        """ takes an optional type by which to filter
            returns a set of objects
        """
        if type_class is None:
            refs = self._shared.all()
        else:
            content_type = ContentType.objects.get_for_model(type_class)
            refs = self._shared.select_related('target_type').filter(
                target_type=content_type
            )
        #return refs
        # this deduping is only neccessary because we had some bad data
        return {r.target for r in refs}

    def get_shared_content(self, type_class=None):
        """ get items 'shared' with self in the activitystream
            takes an optional type by which to filter
            returns a set of objects
        """
        my_content_type = ContentType.objects.get_for_model(self.__class__)
        stream = Action.objects.filter(verb__exact='shared',
                                       target_content_type=my_content_type,
                                       target_object_id=self.id)
        if type_class:
            shared_object_content_type = ContentType.objects.get_for_model(type_class)
            stream = stream.filter( action_object_content_type=shared_object_content_type)

        # this is done as a set in order to maintain the legacy return type.
        return [r.action_object for r in stream]

    def deprecated_get_activity_stream(self, type_class=None):
        shared = self.get_shared_content(type_class)
        if not shared:
            # the empty query would end up returning all rows
            # so we return "nothing" explicitly
            return Action.objects.none()
        query = Q()
        for obj in shared:
            obj_type = ContentType.objects.get_for_model(obj)
            if obj_type.model == 'casereport' and obj.workflow_state != 'live':
                continue
            q = Q(action_object_object_id=obj.id) & \
                Q(action_object_content_type=obj_type)
            query.add(q, Q.OR)
        filtered_actions = Action.objects.filter(query)
        return filtered_actions
