# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0033_auto_20151119_1620'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='dating_count',
            field=models.IntegerField(default=0, db_index=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='photo',
            name='first_dating',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='photo',
            name='latest_dating',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='points',
            name='action',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Geot\xe4\xe4g'), (1, '\xdclepildistus'), (2, 'Foto \xfcleslaadimine'), (3, 'Foto kureerimine'), (4, 'Foto rekureerimine'), (5, 'Dateering'), (6, 'Dateeringu kinnitus')]),
            preserve_default=True,
        ),
    ]
