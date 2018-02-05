# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2018-01-18 21:30
from __future__ import unicode_literals

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0022_auto_20171218_2000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reference',
            name='parsed_data',
            field=jsonfield.fields.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='reference',
            name='raw_data',
            field=jsonfield.fields.JSONField(default=dict),
        ),
    ]