# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2018-07-26 14:16
from __future__ import unicode_literals

from django.db import migrations

from rlp.projects.models import ProjectMembership


def reset_enabled_as_null(*args):
    pms = ProjectMembership.objects.filter(digest_prefs='enabled')
    for pm in pms:
        pm.digest_prefs=None
        pm.save()


def fake_reverse(*args):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0028_membership_to_default_to_global_prefs'),
    ]

    operations = [
        migrations.RunPython(reset_enabled_as_null, reverse_code=fake_reverse)
    ]
