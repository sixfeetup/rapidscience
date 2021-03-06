# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-06-28 17:53
from __future__ import unicode_literals

from django.db import migrations
from django.utils.text import slugify

from casereport.models import SubtypeOption, MolecularAbberation
from taggit.models import Tag

def subtypeoptions_as_tags(apps, schema_editor):
    for so in SubtypeOption.objects.all():
        tag, is_new = Tag.objects.get_or_create(slug=slugify(so.name), defaults={'name':so.name,})


def molecularaberratrions_as_tags(apps, schema_editor):
    for ma in MolecularAbberation.objects.all():
        tag, is_new = Tag.objects.get_or_create(slug=slugify(ma.name), defaults={'name':ma.name,})

class Migration(migrations.Migration):

    dependencies = [
        ('managedtags', '0004_deprecate_unsupprted_tags'),
    ]

    operations = [
        migrations.RunPython(subtypeoptions_as_tags),
        migrations.RunPython(molecularaberratrions_as_tags),
    ]
