# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-10-18 18:21
from __future__ import unicode_literals

from django.db import migrations, models

from ..models import ThreadedComment


def set_shareable(apps, schema_editor):
    """set the shareable flag on existing content
       it should be false if only shared with a closed group
    """
    for obj in ThreadedComment.objects.all():
        closed = []
        for viewer in obj.get_viewers():
            if not hasattr(viewer, 'approval_required'):
                continue
            closed.append(viewer.approval_required)
        if closed and all(closed):
            obj.shareable = False
            obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('discussions', '0008_auto_20170720_1949'),
    ]

    operations = [
        migrations.AddField(
            model_name='threadedcomment',
            name='shareable',
            field=models.BooleanField(default=True, editable=False),
        ),
        # migrations.RunPython(set_shareable),
    ]
