# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0040_auto_20151127_1537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geotag',
            name='map_type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Google kaart'), (1, 'Google satelliit'), (2, 'OpenStreetMap'), (3, 'Juks'), (4, 'No map')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='geotag',
            name='origin',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'M\xe4ng'), (1, 'Kaardivaade'), (2, 'Galerii'), (3, 'P\xfcsiviide'), (4, 'Source')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='geotag',
            name='type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Kaart'), (1, 'EXIF'), (2, 'GPS'), (3, 'Kinnitus'), (4, 'StreetView'), (5, 'Source geotag')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='geotag',
            name='user',
            field=models.ForeignKey(related_name='geotags', blank=True, to='ajapaik.Profile', null=True, on_delete=models.deletion.CASCADE),
            preserve_default=True,
        ),
    ]
