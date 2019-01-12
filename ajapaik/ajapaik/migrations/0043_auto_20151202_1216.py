# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0042_auto_20151130_1151'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='is_film_still_album',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='albumphoto',
            name='type',
            field=models.PositiveSmallIntegerField(default=2, choices=[(0, b'Curated'), (1, b'Re-curated'), (2, b'Manual'), (3, b'Still')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='points',
            name='action',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Geot\xe4\xe4g'), (1, '\xdclepildistus'), (2, 'Foto \xfcleslaadimine'), (3, 'Foto kureerimine'), (4, 'Foto rekureerimine'), (5, 'Dateering'), (6, 'Dateeringu kinnitus'), (7, 'Film still')]),
            preserve_default=True,
        ),
    ]
