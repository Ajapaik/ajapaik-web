# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0070_album_cover_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='latest_rephoto',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
