# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-05-17 23:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('casereport', '0028_call_retraction_revise'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='casereport',
            name='status',
        ),
    ]
