# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-07-20 20:24
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0021_adding_approver_to_project_membership'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectmembership',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projectmembership', to=settings.AUTH_USER_MODEL),
        ),
    ]
