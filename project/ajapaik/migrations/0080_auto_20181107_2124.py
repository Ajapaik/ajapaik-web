# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0079_auto_20171215_1557'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='detected_faces',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='geotag',
            name='origin',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'M\xe4ng'), (1, 'Kaardivaade'), (2, 'Galerii'), (3, 'P\xfcsiviide'), (4, 'Allikas'), (5, '\xdclepildistus')]),
        ),
        migrations.AlterField(
            model_name='geotag',
            name='type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Kaart'), (1, 'EXIF'), (2, 'GPS'), (3, 'Kinnitus'), (4, 'StreetView'), (5, 'Allika geot\xe4\xe4g'), (6, 'Android app')]),
        ),
    ]
