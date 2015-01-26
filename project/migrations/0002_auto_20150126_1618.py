# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_squashed_0011_auto_20150126_1108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geotag',
            name='type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, b'Map'), (1, b'EXIF'), (2, b'GPS')]),
            preserve_default=True,
        ),
    ]
