# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailLog',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=200)),
                ('message_text', models.TextField()),
                ('message_html', models.TextField()),
                ('to_email', models.EmailField(max_length=254)),
                ('date_sent', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
