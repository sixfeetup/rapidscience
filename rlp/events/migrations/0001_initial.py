# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('page_title', models.CharField(max_length=255, blank=True, help_text='Overwrite the title (html title tag)')),
                ('menu_title', models.CharField(max_length=55, blank=True, help_text='Overwrite the title in the menu')),
                ('meta_description', models.CharField(max_length=155, blank=True, help_text='The text displayed in search engines.')),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('description', models.CharField(max_length=500)),
                ('url', models.URLField()),
                ('location', models.CharField(max_length=150)),
                ('image', models.ImageField(upload_to='events')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
            ],
            options={
                'ordering': ['start_date'],
            },
        ),
    ]
