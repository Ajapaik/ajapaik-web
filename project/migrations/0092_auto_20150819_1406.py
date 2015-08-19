# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0091_album_cover_photo_flipped'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='address',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='geotag',
            name='type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Kaart'), (1, 'EXIF'), (2, 'GPS'), (3, 'Kinnitus')]),
            preserve_default=True,
        ),
    ]
