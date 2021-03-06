# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2018-07-02 20:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0018_change_email_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='digest_prefs',
            field=models.CharField(choices=[('enabled', 'Email me a weekly digest of all items shared with me and with groups to which I belong.'), ('disabled', 'Do not email me a weekly digest (*). I will check my Dashboard to view shared items')], default='enabled', max_length=255, verbose_name='Email digest preferences'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email_prefs',
            field=models.CharField(choices=[('user_and_group', 'Email me immediately when an item is shared with me individually or with groups to which I belong.'), ('user_only', 'Email me immediately only when an item is shared with me individually.'), ('disabled', 'Do not send immediate email notifications (*).')], default='disabled', max_length=255, verbose_name='Email notification preferences'),
        ),
    ]
