# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0048_cattag_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='geotag',
            name='map_type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Google map'), (1, 'Google satellite'), (2, 'Open StreetMap')]),
            preserve_default=True,
        ),
    ]
