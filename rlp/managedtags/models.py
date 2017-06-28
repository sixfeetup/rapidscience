from django.db import models
from taggit.models import TagBase, GenericTaggedItemBase
from django.utils.translation import ugettext_lazy as _

class ManagedTag(TagBase):
    approved = models.BooleanField(default=False, blank=True)
    create_date = models.DateTimeField(auto_now_add=True, null=True)
    update_date = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    def __str__(self):
        if not self.approved:
            return "_" + self.name
        return self.name


class TaggedByManagedTag(GenericTaggedItemBase):
    tag = models.ForeignKey(ManagedTag,
                            related_name="%(app_label)s_%(class)s_items")

