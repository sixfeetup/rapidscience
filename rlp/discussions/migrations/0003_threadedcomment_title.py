# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-24 18:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discussions', '0002_auto_20160308_1822'),
    ]

    operations = [
        migrations.AddField(
            model_name='threadedcomment',
            name='title',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
