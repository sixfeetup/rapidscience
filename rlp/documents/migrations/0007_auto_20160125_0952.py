# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0007_auto_20160114_0641'),
        ('documents', '0006_auto_20160112_0320'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='project',
            field=models.ForeignKey(null=True, to='projects.Project'),
        ),
        migrations.AlterField(
            model_name='document',
            name='projects',
            field=models.ManyToManyField(blank=True, related_name='temp', to='projects.Project'),
        ),
    ]
