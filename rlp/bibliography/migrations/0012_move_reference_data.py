from django.db import migrations


'''
Move tags, discussions, and sharing data from ProjectReference to Reference
'''


def move_ref_data(apps, schema_editor):
    Reference = apps.get_model('bibliography', 'Reference')
    ProjectReference = apps.get_model('bibliography', 'ProjectReference')
    ContentType = apps.get_model('contenttypes', 'contenttype')
    SharedContent = apps.get_model('core', 'SharedContent')
    pr_type = ContentType.objects.get_for_model(ProjectReference)
    ref_type = ContentType.objects.get_for_model(Reference)
    for pr in ProjectReference.objects.all():
        ref = pr.reference
        ref.tags = pr.tags
        if hasattr(pr, 'discussions'):
            ref.discussions = pr.discussions
        ref.save()
        # update sharing
        shared_refs = SharedContent.objects.filter(
            target_id=pr.id,
            target_type=pr_type,
        )
        for s_ref in shared_refs:
            s_ref.target_id = ref.id
            s_ref.target_type = ref_type
            s_ref.save()


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0011_share_references'),
    ]

    operations = [migrations.RunPython(move_ref_data)]
