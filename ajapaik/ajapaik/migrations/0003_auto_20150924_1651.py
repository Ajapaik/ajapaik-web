# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0002_auto_20150924_1300'),
    ]

    operations = [
        migrations.AddField(
            model_name='albumphoto',
            name='profile',
            field=models.ForeignKey(blank=True, to='ajapaik.Profile', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='albumphoto',
            name='type',
            field=models.PositiveSmallIntegerField(default=2, choices=[(0, b'Curated'), (1, b'Re-curated'), (2, b'Manual')]),
            preserve_default=True,
        ),
    ]
