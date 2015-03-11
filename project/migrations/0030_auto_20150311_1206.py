# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import project.home.models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0029_album_subalbum_of'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='slug',
            field=models.SlugField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=models.ImageField(max_length=255, null=True, upload_to=project.home.models.PathAndRename(b'uploads'), blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='image_unscaled',
            field=models.ImageField(max_length=255, null=True, upload_to=project.home.models.PathAndRename(b'uploads'), blank=True),
            preserve_default=True,
        ),
    ]
