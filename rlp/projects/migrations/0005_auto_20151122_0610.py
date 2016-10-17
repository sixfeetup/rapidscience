# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_project_goal'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ['order', 'title']},
        ),
        migrations.AlterModelOptions(
            name='topic',
            options={'ordering': ['order']},
        ),
        migrations.AddField(
            model_name='project',
            name='order',
            field=models.PositiveIntegerField(default=0, db_index=True),
        ),
        migrations.AddField(
            model_name='topic',
            name='order',
            field=models.PositiveIntegerField(default=0, db_index=True),
        ),
    ]
