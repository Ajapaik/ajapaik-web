# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0089_photo_muis_media_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='name_de',
            field=models.CharField(max_length=255, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='area',
            name='name_de',
            field=models.CharField(max_length=255, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='catalbum',
            name='subtitle_de',
            field=models.CharField(max_length=255, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='catalbum',
            name='title_de',
            field=models.CharField(max_length=255, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='photo',
            name='description_de',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='photo',
            name='title_de',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
    ]
