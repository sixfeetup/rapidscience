# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-02 17:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0013_remove_document_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='description',
            field=models.TextField(),
        ),
    ]
