# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def populate_document_activity(apps, schema_editor):
    Document = apps.get_model('documents', 'Document')
    File = apps.get_model('documents', 'File')
    Image = apps.get_model('documents', 'Image')
    Link = apps.get_model('documents', 'Link')
    Project = apps.get_model('projects', 'Project')
    from actstream import action
    from actstream import registry
    registry.register(Document)
    registry.register(File)
    registry.register(Image)
    registry.register(Link)
    registry.register(Project)
    for doc in File.objects.all():
        if doc.projects.count() == 1:
            target = doc.projects.first()
        else:
            target = None
        action.send(doc.owner, verb='uploaded', action_object=doc, target=target, timestamp=doc.date_added)
    for doc in Image.objects.all():
        if doc.projects.count() == 1:
            target = doc.projects.first()
        else:
            target = None
        action.send(doc.owner, verb='uploaded', action_object=doc, target=target, timestamp=doc.date_added)
    for link in Link.objects.all():
        if link.projects.count() == 1:
            target = link.projects.first()
        else:
            target = None
        action.send(link.owner, verb='added', action_object=link, target=target, timestamp=link.date_added)


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0004_link'),
        ('projects', '0006_auto_20151201_2159'),
        ('actstream', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_document_activity)
    ]
