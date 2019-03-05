# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0087_auto_20190207_2339'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Newsletter',
        ),
        migrations.AlterField(
            model_name='album',
            name='gender',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(1, 'Naine'), (0, 'Mees')]),
        ),
        migrations.AlterField(
            model_name='geotag',
            name='type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Kaart'), (1, 'EXIF'), (2, 'GPS'), (3, 'Kinnitus'), (4, 'StreetView'), (5, 'Allika geotääg'), (6, 'Android rakendus')]),
        ),
    ]
