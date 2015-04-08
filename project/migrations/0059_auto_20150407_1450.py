# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0058_remove_profile_avatar_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geotag',
            name='map_type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Google kaart'), (1, 'Google satelliit'), (2, 'OpenStreetMap')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='geotag',
            name='origin',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'M\xe4ng'), (1, 'Kaardivaade'), (2, 'Galerii')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='lat',
            field=models.FloatField(blank=True, null=True, db_index=True, validators=[django.core.validators.MinValueValidator(-85.05115), django.core.validators.MaxValueValidator(85)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='lon',
            field=models.FloatField(blank=True, null=True, db_index=True, validators=[django.core.validators.MinValueValidator(-180), django.core.validators.MaxValueValidator(180)]),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='albumphoto',
            unique_together=set([]),
        ),
    ]
