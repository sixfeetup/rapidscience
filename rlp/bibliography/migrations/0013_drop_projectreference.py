# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-05-05 13:54
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0012_move_reference_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectreference',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='projectreference',
            name='reference',
        ),
        migrations.RemoveField(
            model_name='projectreference',
            name='tags',
        ),
        migrations.DeleteModel(
            name='ProjectReference',
        ),
    ]
