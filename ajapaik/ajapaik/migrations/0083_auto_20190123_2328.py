# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0082_auto_20190120_1451'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tour',
            name='photos',
        ),
        migrations.RemoveField(
            model_name='tour',
            name='user',
        ),
        migrations.AlterUniqueTogether(
            name='tourgroup',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='tourgroup',
            name='members',
        ),
        migrations.RemoveField(
            model_name='tourgroup',
            name='tour',
        ),
        migrations.RemoveField(
            model_name='tourphoto',
            name='photo',
        ),
        migrations.RemoveField(
            model_name='tourphoto',
            name='tour',
        ),
        migrations.RemoveField(
            model_name='tourphotoorder',
            name='photo',
        ),
        migrations.RemoveField(
            model_name='tourphotoorder',
            name='tour',
        ),
        migrations.RemoveField(
            model_name='tourrephoto',
            name='original',
        ),
        migrations.RemoveField(
            model_name='tourrephoto',
            name='tour',
        ),
        migrations.RemoveField(
            model_name='tourrephoto',
            name='user',
        ),
        migrations.AlterUniqueTogether(
            name='touruniqueview',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='touruniqueview',
            name='profile',
        ),
        migrations.RemoveField(
            model_name='touruniqueview',
            name='tour',
        ),
        migrations.RemoveField(
            model_name='photo',
            name='then_and_now_rephoto',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='send_then_and_now_photos_to_ajapaik',
        ),
        migrations.AlterField(
            model_name='album',
            name='is_public',
            field=models.BooleanField(verbose_name='Is public', default=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='name',
            field=models.CharField(verbose_name='Name', max_length=255),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_de',
            field=models.CharField(verbose_name='Name', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_en',
            field=models.CharField(verbose_name='Name', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_et',
            field=models.CharField(verbose_name='Name', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_fi',
            field=models.CharField(verbose_name='Name', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_nl',
            field=models.CharField(verbose_name='Name', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_no',
            field=models.CharField(verbose_name='Name', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_ru',
            field=models.CharField(verbose_name='Name', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_sv',
            field=models.CharField(verbose_name='Name', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='open',
            field=models.BooleanField(verbose_name='Is open', default=False),
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
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Game'), (1, 'Map view'), (2, 'Gallery'), (3, 'Permalink'), (4, 'Source'), (5, 'Rephoto')]),
        ),
        migrations.AlterField(
            model_name='geotag',
            name='type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Map'), (1, 'EXIF'), (2, 'GPS'), (3, 'Confirmation'), (4, 'StreetView'), (5, 'Source geotag'), (6, 'Android app')]),
        ),
        migrations.AlterField(
            model_name='photo',
            name='author',
            field=models.CharField(verbose_name='Author', max_length=255, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='points',
            name='action',
            field=models.PositiveSmallIntegerField(db_index=True, choices=[(0, 'Geotag'), (1, 'Rephoto'), (2, 'Photo upload'), (3, 'Photo curation'), (4, 'Photo re-curation'), (5, 'Dating'), (6, 'Dating confirmation'), (7, 'Film still')]),
        ),
        migrations.DeleteModel(
            name='Tour',
        ),
        migrations.DeleteModel(
            name='TourGroup',
        ),
        migrations.DeleteModel(
            name='TourPhoto',
        ),
        migrations.DeleteModel(
            name='TourPhotoOrder',
        ),
        migrations.DeleteModel(
            name='TourRephoto',
        ),
        migrations.DeleteModel(
            name='TourUniqueView',
        ),
    ]
