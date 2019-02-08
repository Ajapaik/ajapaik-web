# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0050_auto_20151216_1125'),
    ]

    operations = [
        migrations.AddField(
            model_name='tour',
            name='photo_set_type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Fixed photo set'), (1, 'Any photos')]),
            preserve_default=True,
        ),
    ]
