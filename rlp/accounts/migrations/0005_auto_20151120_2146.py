# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_remove_user_department'),
    ]

    operations = [
        migrations.AddField(
            model_name='institution',
            name='banner_image',
            field=models.ImageField(upload_to='institutions', blank=True),
        ),
        migrations.AddField(
            model_name='institution',
            name='thumbnail_image',
            field=models.ImageField(upload_to='institutions', blank=True),
        ),
    ]
