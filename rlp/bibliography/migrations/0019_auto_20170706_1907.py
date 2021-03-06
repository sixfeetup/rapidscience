# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-07-06 19:07
from __future__ import unicode_literals

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0018_auto_20170630_1455'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userreference',
            name='mtags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A Comma separated list of UNAPPROVED tags.', through='managedtags.TaggedByManagedTag', to='managedtags.ManagedTag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='userreference',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AlterUniqueTogether(
            name='userreference',
            unique_together=set([]),
        ),
    ]
