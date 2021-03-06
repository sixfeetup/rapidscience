# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-20 20:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_remove_user_tags_following'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstitutionDomain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(max_length=200)),
                ('institution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.Institution')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='institutiondomain',
            unique_together=set([('institution', 'domain')]),
        ),
    ]
