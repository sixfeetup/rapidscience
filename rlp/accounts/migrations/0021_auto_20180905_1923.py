# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2018-09-05 19:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0020_auto_20180831_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='digest_prefs',
            field=models.CharField(choices=[('enabled', 'Email me a weekly digest of all items shared with me and with groups to which I belong.'), ('disabled', 'Do not email me a weekly digest (*). I will check my Dashboard to view shared items.')], default='enabled', max_length=255, verbose_name='Email digest preferences'),
        ),
    ]
