# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-04-04 20:33
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('casereport', '0008_auto_20170328_1943'),
    ]

    operations = [
        migrations.AddField(
            model_name='casereport',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True, db_index=True, default=datetime.datetime(2017, 4, 4, 20, 33, 29, 235624, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='casereport',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2017, 4, 4, 20, 33, 34, 722823, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
