# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0006_auto_20151201_2159'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('taggit', '0002_auto_20150616_2121'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('date_added', models.DateTimeField(db_index=True, auto_now=True)),
            ],
            options={
                'ordering': ['-date_added'],
            },
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('document_ptr', models.OneToOneField(parent_link=True, primary_key=True, to='documents.Document', auto_created=True, serialize=False)),
                ('file', models.FileField(upload_to='docs/%Y/%m/%d')),
                ('working_document', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=('documents.document',),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('document_ptr', models.OneToOneField(parent_link=True, primary_key=True, to='documents.Document', auto_created=True, serialize=False)),
                ('image', models.ImageField(height_field='height', width_field='width', max_length=255, upload_to='docs/images/%Y/%m/%d')),
                ('height', models.PositiveIntegerField()),
                ('width', models.PositiveIntegerField()),
            ],
            options={
                'abstract': False,
            },
            bases=('documents.document',),
        ),
        migrations.AddField(
            model_name='document',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='document',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_documents.document_set+', to='contenttypes.ContentType', editable=False, null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='projects',
            field=models.ManyToManyField(blank=True, to='projects.Project'),
        ),
        migrations.AddField(
            model_name='document',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
