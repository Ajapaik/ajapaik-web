# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0043_auto_20151202_1216'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='author',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='video',
            name='source',
            field=models.ForeignKey(blank=True, to='ajapaik.Source', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='video',
            name='source_key',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='video',
            name='source_url',
            field=models.URLField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='geotag',
            name='map_type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Google kaart'), (1, 'Google satelliit'), (2, 'OpenStreetMap'), (3, 'Juks'), (4, 'Pole kaardilt')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='geotag',
            name='origin',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'M\xe4ng'), (1, 'Kaardivaade'), (2, 'Galerii'), (3, 'P\xfcsiviide'), (4, 'Allikas')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='geotag',
            name='type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Kaart'), (1, 'EXIF'), (2, 'GPS'), (3, 'Kinnitus'), (4, 'StreetView'), (5, 'Allika geot\xe4\xe4g')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='points',
            name='action',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Geot\xe4\xe4g'), (1, '\xdclepildistus'), (2, 'Foto \xfcleslaadimine'), (3, 'Foto kureerimine'), (4, 'Foto rekureerimine'), (5, 'Dateering'), (6, 'Dateeringu kinnitus'), (7, 'Filmikaader')]),
            preserve_default=True,
        ),
    ]
