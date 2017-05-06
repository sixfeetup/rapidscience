# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-05-05 13:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('casereport', '0017_change_default_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='casereport',
            name='admin_approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='casereport',
            name='author_approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='casereport',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('processing', 'Processing'), ('ready', 'Ready to Review'), ('approved', 'Approved'), ('changes', 'Need Changes'), ('reviewed', 'Reviewed'), ('edited', 'Edited')], default='draft', help_text='Workflow State', max_length=50),
        ),
    ]