# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0071_photo_latest_rephoto'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='latest_comment',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='photo',
            name='latest_geotag',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
