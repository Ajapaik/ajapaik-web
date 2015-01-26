# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import project.home.models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0005_auto_20150106_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=models.ImageField(null=True, upload_to=project.home.models.PathAndRename(b'uploads'), blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='image_unscaled',
            field=models.ImageField(null=True, upload_to=project.home.models.PathAndRename(b'uploads'), blank=True),
            preserve_default=True,
        ),
    ]
