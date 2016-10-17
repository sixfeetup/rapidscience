# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import cms.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0012_auto_20150607_2207'),
        ('projects', '0002_auto_20151118_0252'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='bibliography',
            field=cms.models.fields.PlaceholderField(slotname='bibliography', to='cms.Placeholder', null=True, editable=False),
        ),
    ]
