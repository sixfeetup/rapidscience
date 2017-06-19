# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-06-15 19:59
from __future__ import unicode_literals

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('casereport', '0037_aberrations_update'),
    ]

    operations = [
        migrations.AddField(
            model_name='casereport',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]