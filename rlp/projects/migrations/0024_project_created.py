# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2018-03-26 20:45
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0023_allow_blank_approvers_on_existing_memberships'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2018, 3, 9, 20, 45, 9, 208718, tzinfo=utc)),
            preserve_default=False,
        ),
    ]