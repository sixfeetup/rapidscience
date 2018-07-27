# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2018-07-26 14:33
from __future__ import unicode_literals

from django.db import migrations, models

from rlp.accounts.models import User
from rlp.projects.models import ProjectMembership


def reset_prefs(*args):
    pms = ProjectMembership.objects.filter(digest_prefs='user_and_group')
    for pm in pms:
        pm.digest_prefs = 'enabled'
        pm.save()

    pms = ProjectMembership.objects.filter(email_prefs='digest')
    for pm in pms:
        pm.digest_prefs = 'disabled'
        pm.save()

    accounts = User.objects.filter(email_prefs='digest') # this value is a deprecated default.
    for user in accounts:
        user.email_prefs = 'disabled'
        user.save()


def fake_reverse(*args):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0029_reset_default_email_prefs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectmembership',
            name='digest_prefs',
            field=models.CharField(blank=True, choices=[('enabled', 'Email me a weekly digest of all items shared with me and with groups to which I belong.'), ('disabled', 'Do not email me a weekly digest (*). I will check my Dashboard to view shared items')], max_length=255, null=True, verbose_name='Email digest preferences'),
        ),
        migrations.RunPython(reset_prefs, reverse_code=fake_reverse)
    ]
