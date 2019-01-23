# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0083_auto_20190123_2328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='albumphoto',
            name='type',
            field=models.PositiveSmallIntegerField(db_index=True, default=2, choices=[(0, 'Curated'), (1, 'Re-curated'), (2, 'Manual'), (3, 'Still'), (4, 'Uploaded'), (5, 'Face tagged')]),
        ),
    ]
