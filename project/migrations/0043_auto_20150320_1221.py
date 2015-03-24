# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0042_auto_20150318_1720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geotag',
            name='hint_used',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='geotag',
            name='is_correct',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='geotag',
            name='lat',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(-85), django.core.validators.MaxValueValidator(85)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='geotag',
            name='lon',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(-180), django.core.validators.MaxValueValidator(180)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='geotag',
            name='origin',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Game'), (1, 'Map view'), (2, 'Grid')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='geotag',
            name='score',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
