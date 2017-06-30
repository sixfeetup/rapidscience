# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-06-30 14:55
from __future__ import unicode_literals

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('discussions', '0006_auto_20170627_2052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='threadedcomment',
            name='mtags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A Comma separated list of UNAPPROVED tags.', through='managedtags.TaggedByManagedTag', to='managedtags.ManagedTag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='threadedcomment',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
