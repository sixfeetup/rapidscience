# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def populate_project(apps, schema_editor):
    Document = apps.get_model('documents', 'Document')
    for doc in Document.objects.all():
        doc.project = doc.projects.first()
        doc.save()


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0007_auto_20160125_0952'),
    ]

    operations = [
        migrations.RunPython(populate_project)
    ]
