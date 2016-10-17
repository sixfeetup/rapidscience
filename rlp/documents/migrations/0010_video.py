# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import embed_video.fields


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0009_auto_20160125_0955'),
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('document_ptr', models.OneToOneField(parent_link=True, to='documents.Document', serialize=False, auto_created=True, primary_key=True)),
                ('share_link', embed_video.fields.EmbedVideoField(help_text='Should be a Youtube or Vimeo share link e.g. https://youtu.be/xyz123')),
            ],
            options={
                'abstract': False,
            },
            bases=('documents.document',),
        ),
    ]
