# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0043_auto_20150320_1221'),
    ]

    operations = [
        migrations.AddField(
            model_name='geotag',
            name='azimuth_correct',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
