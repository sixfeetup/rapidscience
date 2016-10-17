# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0003_auto_20151202_1846'),
    ]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('document_ptr', models.OneToOneField(to='documents.Document', serialize=False, parent_link=True, primary_key=True, auto_created=True)),
                ('url', models.URLField()),
            ],
            options={
                'abstract': False,
            },
            bases=('documents.document',),
        ),
    ]
