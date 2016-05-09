# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0068_auto_20160509_1541'),
    ]

    operations = [
        migrations.AddField(
            model_name='licence',
            name='is_public',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='albumphoto',
            name='type',
            field=models.PositiveSmallIntegerField(default=2, choices=[(0, b'Curated'), (1, b'Re-curated'), (2, b'Manual'), (3, b'Still'), (4, b'Uploaded')]),
            preserve_default=True,
        ),
    ]
