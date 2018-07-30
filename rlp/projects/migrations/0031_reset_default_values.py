# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2018-07-30 20:47
from __future__ import unicode_literals

from django.db import migrations
from rlp.projects.models import ProjectMembership


def reset_defaults_values_ep(*args):
    pms = ProjectMembership.objects.filter(email_prefs='disabled', user__email_prefs='disabled')
    for pm in pms:
        pm.email_prefs = None
        pm.save()


def reset_defaults_values_dp(*args):
    pms = ProjectMembership.objects.filter(digest_prefs='enabled', user__digest_prefs='enabled')
    for pm in pms:
        pm.digest_prefs = None
        pm.save()


def fake_reverse(*args):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0030_fix_default_digest_prefs'),
    ]

    operations = [
        migrations.RunPython(reset_defaults_values_ep, reverse_code=fake_reverse),
        migrations.RunPython(reset_defaults_values_dp, reverse_code=fake_reverse),
    ]