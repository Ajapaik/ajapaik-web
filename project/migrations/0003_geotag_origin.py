# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0002_photo_geography'),
    ]

    operations = [
        migrations.AddField(
            model_name='geotag',
            name='origin',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, b'Game'), (1, b'Map'), (2, b'Grid')]),
            preserve_default=True,
        ),
    ]
