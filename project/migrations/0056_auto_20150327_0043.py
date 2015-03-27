# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0055_auto_20150324_1312'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='credentialsmodel',
            name='id',
        ),
        migrations.DeleteModel(
            name='CredentialsModel',
        ),
        migrations.RemoveField(
            model_name='flowmodel',
            name='id',
        ),
        migrations.DeleteModel(
            name='FlowModel',
        ),
        migrations.RemoveField(
            model_name='usermapview',
            name='photo',
        ),
        migrations.RemoveField(
            model_name='usermapview',
            name='user_profile',
        ),
        migrations.DeleteModel(
            name='UserMapView',
        ),
        migrations.AlterModelOptions(
            name='skip',
            options={},
        ),
        migrations.AlterField(
            model_name='area',
            name='name',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='area',
            name='name_en',
            field=models.CharField(max_length=255, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='area',
            name='name_et',
            field=models.CharField(max_length=255, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='area',
            name='name_fi',
            field=models.CharField(max_length=255, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='area',
            name='name_nl',
            field=models.CharField(max_length=255, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='area',
            name='name_ru',
            field=models.CharField(max_length=255, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='area',
            name='name_sv',
            field=models.CharField(max_length=255, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='catalbum',
            name='image',
            field=models.ImageField(max_length=255, upload_to=b'cat'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='catphoto',
            name='image',
            field=models.ImageField(max_length=255, upload_to=b'cat'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='geotag',
            name='azimuth_score',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='geotag',
            name='lat',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(-85.05115), django.core.validators.MaxValueValidator(85)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='geotag',
            name='map_type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Google kaart'), (1, 'Google satellite'), (2, 'OpenStreetMap')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='geotag',
            name='score',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='licence',
            name='url',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='cam_scale_factor',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.5), django.core.validators.MaxValueValidator(4.0)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='date_text',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='description',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='description_en',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='description_et',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='description_fi',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='description_nl',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='description_ru',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='description_sv',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='id',
            field=models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=models.ImageField(max_length=255, null=True, upload_to=b'uploads', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='image_unscaled',
            field=models.ImageField(max_length=255, null=True, upload_to=b'uploads', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='lat',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(-85.05115), django.core.validators.MaxValueValidator(85)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='lon',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(-180), django.core.validators.MaxValueValidator(180)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='points',
            name='points',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='albumphoto',
            unique_together=set([('album', 'photo')]),
        ),
        migrations.RemoveField(
            model_name='albumphoto',
            name='sort_order',
        ),
        migrations.RemoveField(
            model_name='albumphoto',
            name='notes',
        ),
        migrations.AlterUniqueTogether(
            name='catphoto',
            unique_together=set([('source', 'source_key')]),
        ),
        migrations.AlterUniqueTogether(
            name='points',
            unique_together=set([('user', 'geotag')]),
        ),
        migrations.RemoveField(
            model_name='points',
            name='action_reference',
        ),
    ]
