# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0008_auto_20160125_0952'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='projects',
        ),
        migrations.AlterField(
            model_name='document',
            name='project',
            field=models.ForeignKey(to='projects.Project'),
        ),
    ]
