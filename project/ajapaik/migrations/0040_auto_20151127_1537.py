# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0039_video_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='height',
            field=models.IntegerField(default=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='video',
            name='width',
            field=models.IntegerField(default=100),
            preserve_default=False,
        ),
    ]
