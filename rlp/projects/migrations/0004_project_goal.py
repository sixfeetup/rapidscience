# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_project_bibliography'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='goal',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
