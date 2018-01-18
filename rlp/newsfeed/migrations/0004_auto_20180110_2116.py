# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2018-01-10 21:16
from __future__ import unicode_literals

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('newsfeed', '0003_auto_20160218_0050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsitem',
            name='data',
            field=jsonfield.fields.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='newsitem',
            name='library',
            field=jsonfield.fields.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='newsitem',
            name='links',
            field=jsonfield.fields.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='newsitem',
            name='meta',
            field=jsonfield.fields.JSONField(default=dict),
        ),
    ]
