# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0063_tour_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tour',
            name='name',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tour',
            name='photo_set_type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(1, 'Avatud tuur'), (0, 'Valitud fotode tuur'), (2, 'Tuur juhuslikult valitud piltidega Sinu l\xe4hikonnast')]),
            preserve_default=True,
        ),
    ]
