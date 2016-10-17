# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import filer.fields.image


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20151116_1914'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('filer', '0002_auto_20150606_2003'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('page_title', models.CharField(help_text='Overwrite the title (html title tag)', blank=True, max_length=255)),
                ('menu_title', models.CharField(help_text='Overwrite the title in the menu', blank=True, max_length=55)),
                ('meta_description', models.CharField(help_text='The text displayed in search engines.', blank=True, max_length=155)),
                ('slug', models.SlugField(unique=True, max_length=255)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('cover_photo', filer.fields.image.FilerImageField(null=True, blank=True, related_name='project_photo', to='filer.Image')),
                ('institution', models.ForeignKey(null=True, blank=True, to='accounts.Institution')),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='ProjectMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('project', models.ForeignKey(to='projects.Project')),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('page_title', models.CharField(help_text='Overwrite the title (html title tag)', blank=True, max_length=255)),
                ('menu_title', models.CharField(help_text='Overwrite the title in the menu', blank=True, max_length=55)),
                ('meta_description', models.CharField(help_text='The text displayed in search engines.', blank=True, max_length=155)),
                ('slug', models.SlugField(unique=True, max_length=255)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='projectmembership',
            name='role',
            field=models.ForeignKey(null=True, blank=True, to='projects.Role'),
        ),
        migrations.AddField(
            model_name='projectmembership',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='project',
            name='topic',
            field=models.ForeignKey(null=True, blank=True, to='projects.Topic'),
        ),
        migrations.AddField(
            model_name='project',
            name='users',
            field=models.ManyToManyField(related_name='projects', to=settings.AUTH_USER_MODEL, through='projects.ProjectMembership'),
        ),
    ]
