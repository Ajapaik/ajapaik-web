# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0003_geotag_geography'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='geography',
            field=django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, geography=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='album',
            name='lat',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='album',
            name='lon',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
