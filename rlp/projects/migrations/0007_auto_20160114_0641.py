# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0006_auto_20151201_2159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='goal',
            field=models.CharField(max_length=450, blank=True),
        ),
    ]
