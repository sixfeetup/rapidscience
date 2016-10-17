# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_auto_20151122_0610'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='role',
            options={'ordering': ['order']},
        ),
        migrations.AddField(
            model_name='role',
            name='order',
            field=models.PositiveIntegerField(default=0, db_index=True),
        ),
    ]
