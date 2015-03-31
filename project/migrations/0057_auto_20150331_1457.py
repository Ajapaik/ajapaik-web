# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0056_auto_20150327_0043'),
    ]

    operations = [
        migrations.RenameField(
            model_name='album',
            old_name='is_public_mutable',
            new_name='open',
        ),
        migrations.AlterField(
            model_name='geotag',
            name='origin',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Game'), (1, 'Kaardivaade'), (2, 'Grid')]),
            preserve_default=True,
        ),
    ]
