# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0036_auto_20151127_1437'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='cover_image',
            field=models.ImageField(height_field=b'cover_image_height', width_field=b'cover_image_width', null=True, upload_to=b'videos/covers', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='video',
            name='cover_image_height',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='video',
            name='cover_image_width',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
