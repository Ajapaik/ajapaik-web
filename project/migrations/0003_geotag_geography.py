# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0002_auto_20150126_1618'),
    ]

    operations = [
        migrations.AddField(
            model_name='geotag',
            name='geography',
            field=django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, geography=True, blank=True),
            preserve_default=True,
        ),
    ]
