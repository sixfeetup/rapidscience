# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-07-13 21:15
from __future__ import unicode_literals

from django.db import migrations
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0019_auto_20170705_2115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectmembership',
            name='state',
            field=django_fsm.FSMField(choices=[('moderator', 'Moderator'), ('member', 'Member'), ('pending', 'Applicant'), ('ignored', 'Ignored Applicant')], default='pending', max_length=50),
        ),
    ]
