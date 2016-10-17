# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-18 00:19
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsfeed', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(db_index=True, max_length=100, unique=True)),
                ('itemType', models.CharField(db_index=True, max_length=100)),
                ('version', models.IntegerField()),
                ('date_added', models.DateTimeField(db_index=True)),
                ('meta', django.contrib.postgres.fields.jsonb.JSONField()),
                ('data', django.contrib.postgres.fields.jsonb.JSONField()),
                ('library', django.contrib.postgres.fields.jsonb.JSONField()),
                ('links', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
            options={
                'ordering': ['-date_added'],
            },
        ),
    ]
