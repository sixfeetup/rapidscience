from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from taggit.models import Tag
from rlp.managedtags.models import ManagedTag


@receiver(post_save, sender=ManagedTag, )
def migrate_mtag_to_tag(sender, instance, **kwargs):
    mtag = instance
    if mtag.approved:
        # create an analog Tag for the Mtag
        tag,is_new = Tag.objects.get_or_create(slug=mtag.slug,
                                               defaults={'name':mtag.name})
        if is_new:
            tag.save()
        # add that tag to everyone using the approved MTag
        for obj in mtag.managedtags_taggedbymanagedtag_items.all():
            obj.content_object.tags.add( tag )
            obj.content_object.save()
        # remove the mtag from everyone
        for obj in mtag.managedtags_taggedbymanagedtag_items.all():
            obj.content_object.mtags.remove( mtag )
        # now the mtag is no longer needed, but we'll keep it so that
        # its approval state can be referenced and used as a mechanism to
        # auto replace it with a taggit Tag
        #mtag.delete()

@receiver(pre_delete, sender=Tag)
def deprecate_tag_to_mtag(sender, instance, **kwargs):
    print("deprecate_tag_to_mtag")
    tag = instance

    # create deprecated mtag
    mtag, is_new = ManagedTag.objects.get_or_create(slug=tag.slug,
                                                    defaults={'name': tag.name})

    print( "deprecating", tag, "to", mtag)
    # force it to unapproved
    mtag.approved = False
    mtag.save()

    # move tag on tagged items
    for tagged_item in tag.taggit_taggeditem_items.all():
        tagged_item.content_object.tags.remove(tag)
        tagged_item.content_object.mtags.add(mtag)
        tagged_item.content_object.save()
