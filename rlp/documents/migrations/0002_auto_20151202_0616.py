# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2015, 12, 2, 6, 16, 0, 341474, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='document',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]
