# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0051_auto_20150323_1425'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='azimuth_confidence',
            field=models.FloatField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='confidence',
            field=models.FloatField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
    ]
