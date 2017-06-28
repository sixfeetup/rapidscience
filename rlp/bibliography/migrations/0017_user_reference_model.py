# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-06-28 19:35
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('managedtags', '0005_subtypes_and_aberrations_as_tags'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bibliography', '0016_auto_20170627_2052'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserReference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('description', models.CharField(blank=True, max_length=2000)),
                ('mtags', taggit.managers.TaggableManager(help_text='A Comma separated list of UNAPPROVED tags.', through='managedtags.TaggedByManagedTag', to='managedtags.ManagedTag', verbose_name='Tags')),
                ('reference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bibliography.Reference')),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='userreference',
            unique_together=set([('user', 'reference')]),
        ),
    ]
