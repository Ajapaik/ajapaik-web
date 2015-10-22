# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0008_auto_20150930_1512'),
    ]

    operations = [
        migrations.RenameField(
            model_name='photo',
            old_name='muis_id',
            new_name='external_id',
        ),
        migrations.RenameField(
            model_name='photo',
            old_name='muis_media_id',
            new_name='external_sub_id',
        ),
        migrations.AlterField(
            model_name='geotag',
            name='origin',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'M\xe4ng'), (1, 'Kaardivaade'), (2, 'Gallery'), (3, 'Permalink')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photolike',
            name='profile',
            field=models.ForeignKey(related_name='likes', to='ajapaik.Profile'),
            preserve_default=True,
        ),
    ]
