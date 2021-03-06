# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-20 20:23
from __future__ import unicode_literals

from django.db import migrations


def mark_approval_required(apps, schema_editor):
    Project = apps.get_model('projects', 'Project')
    Project.objects.update(approval_required=True)


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0011_project_approval_required'),
    ]

    operations = [
        migrations.RunPython(mark_approval_required)
    ]
