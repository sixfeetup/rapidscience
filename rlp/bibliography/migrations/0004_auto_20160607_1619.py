# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-07 16:19
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bibliography', '0003_auto_20160323_0229'),
    ]

    operations = [
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('reference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bibliography.Reference')),
            ],
        ),
        migrations.AddField(
            model_name='reference',
            name='authors',
            field=models.ManyToManyField(through='bibliography.Publication', to=settings.AUTH_USER_MODEL),
        ),
    ]
