# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-07-05 15:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_user_banner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='orcid',
        ),
    ]
