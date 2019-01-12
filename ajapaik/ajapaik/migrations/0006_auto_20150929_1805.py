# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0005_photo_like_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='first_like',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='photo',
            name='latest_like',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
