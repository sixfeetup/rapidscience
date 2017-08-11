# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-04-07 15:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('casereport', '0011_auto_20170407_1455'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aberration',
            name='crdbbase_ptr',
        ),
        migrations.AlterField(
            model_name='casereport',
            name='aberrations',
            field=models.ManyToManyField(blank=True, to='casereport.MolecularAbberation'),
        ),
        migrations.DeleteModel(
            name='Aberration',
        ),
    ]
