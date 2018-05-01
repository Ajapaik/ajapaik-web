# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0079_auto_20171215_1557'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='description',
            field=models.TextField(max_length=2047, null=True, verbose_name='Description', blank=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='is_public',
            field=models.BooleanField(default=True, verbose_name='Is public'),
        ),
        migrations.AlterField(
            model_name='album',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_de',
            field=models.CharField(max_length=255, null=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_en',
            field=models.CharField(max_length=255, null=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_et',
            field=models.CharField(max_length=255, null=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_fi',
            field=models.CharField(max_length=255, null=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_nl',
            field=models.CharField(max_length=255, null=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_no',
            field=models.CharField(max_length=255, null=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_ru',
            field=models.CharField(max_length=255, null=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_sv',
            field=models.CharField(max_length=255, null=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='album',
            name='open',
            field=models.BooleanField(default=False, verbose_name='Is open'),
        ),
        migrations.AlterField(
            model_name='dating',
            name='end_accuracy',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(0, 'Day'), (1, 'Month'), (2, 'Year')]),
        ),
        migrations.AlterField(
            model_name='dating',
            name='start_accuracy',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(0, 'Day'), (1, 'Month'), (2, 'Year')]),
        ),
        migrations.AlterField(
            model_name='geotag',
            name='map_type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Google map'), (1, 'Google satellite'), (2, 'OpenStreetMap'), (3, 'Juks'), (4, 'No map')]),
        ),
        migrations.AlterField(
            model_name='geotag',
            name='origin',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Game'), (1, 'Map view'), (2, 'Gallery'), (3, 'Permalink'), (4, 'Source')]),
        ),
        migrations.AlterField(
            model_name='geotag',
            name='type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Map'), (1, 'EXIF'), (2, 'GPS'), (3, 'Confirmation'), (4, 'StreetView'), (5, 'Source geotag')]),
        ),
        migrations.AlterField(
            model_name='photo',
            name='author',
            field=models.CharField(max_length=255, null=True, verbose_name='Author', blank=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='description',
            field=models.TextField(null=True, verbose_name='Description', blank=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='description_de',
            field=models.TextField(null=True, verbose_name='Description', blank=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='description_en',
            field=models.TextField(null=True, verbose_name='Description', blank=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='description_et',
            field=models.TextField(null=True, verbose_name='Description', blank=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='description_fi',
            field=models.TextField(null=True, verbose_name='Description', blank=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='description_nl',
            field=models.TextField(null=True, verbose_name='Description', blank=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='description_no',
            field=models.TextField(null=True, verbose_name='Description', blank=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='description_ru',
            field=models.TextField(null=True, verbose_name='Description', blank=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='description_sv',
            field=models.TextField(null=True, verbose_name='Description', blank=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=models.ImageField(height_field=b'height', width_field=b'width', upload_to=b'uploads', max_length=255, blank=True, null=True, verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='points',
            name='action',
            field=models.PositiveSmallIntegerField(db_index=True, choices=[(0, 'Geotag'), (1, 'Rephoto'), (2, 'Photo upload'), (3, 'Photo curation'), (4, 'Photo re-curation'), (5, 'Dating'), (6, 'Dating confirmation'), (7, 'Film still')]),
        ),
        migrations.AlterField(
            model_name='tour',
            name='photo_set_type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(1, 'Open tour'), (0, 'Fixed photo set'), (2, 'Random with nearby pictures')]),
        ),
    ]
