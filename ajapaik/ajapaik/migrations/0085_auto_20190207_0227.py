# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0084_auto_20190124_0015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='is_public',
            field=models.BooleanField(verbose_name='On avalik', default=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='name',
            field=models.CharField(verbose_name='Pealkiri', max_length=255),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_de',
            field=models.CharField(verbose_name='Pealkiri', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_en',
            field=models.CharField(verbose_name='Pealkiri', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_et',
            field=models.CharField(verbose_name='Pealkiri', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_fi',
            field=models.CharField(verbose_name='Pealkiri', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_nl',
            field=models.CharField(verbose_name='Pealkiri', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_no',
            field=models.CharField(verbose_name='Pealkiri', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_ru',
            field=models.CharField(verbose_name='Pealkiri', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_sv',
            field=models.CharField(verbose_name='Pealkiri', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='open',
            field=models.BooleanField(verbose_name='On avatud (kõik saavad pilte lisada)', default=False),
        ),
        migrations.AlterField(
            model_name='dating',
            name='end_accuracy',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(0, 'Päev'), (1, 'Kuu'), (2, 'Aasta')]),
        ),
        migrations.AlterField(
            model_name='dating',
            name='start_accuracy',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(0, 'Päev'), (1, 'Kuu'), (2, 'Aasta')]),
        ),
        migrations.AlterField(
            model_name='geotag',
            name='map_type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Google kaart'), (1, 'Google satelliit'), (2, 'OpenStreetMap'), (3, 'Juks'), (4, 'Pole kaardilt')]),
        ),
        migrations.AlterField(
            model_name='geotag',
            name='origin',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Mäng'), (1, 'Kaardivaade'), (2, 'Galerii'), (3, 'Püsiviide'), (4, 'Allikas'), (5, 'Ülepildistus')]),
        ),
        migrations.AlterField(
            model_name='geotag',
            name='type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Kaart'), (1, 'EXIF'), (2, 'GPS'), (3, 'Kinnitus'), (4, 'StreetView'), (5, 'Allika geotääg'), (6, 'Android app')]),
        ),
        migrations.AlterField(
            model_name='photo',
            name='author',
            field=models.CharField(verbose_name='Autor', max_length=255, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='points',
            name='action',
            field=models.PositiveSmallIntegerField(db_index=True, choices=[(0, 'Geotääg'), (1, 'Ülepildistus'), (2, 'Foto üleslaadimine'), (3, 'Foto kureerimine'), (4, 'Foto rekureerimine'), (5, 'Dateering'), (6, 'Dateeringu kinnitus'), (7, 'Filmikaader')]),
        ),
    ]
