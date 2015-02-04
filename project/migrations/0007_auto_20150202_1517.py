# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0006_photo_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='licence',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='album',
            name='atype',
            field=models.PositiveSmallIntegerField(choices=[(0, b'Frontpage'), (1, b'Favorites'), (2, b'Collection'), (3, b'Area')]),
            preserve_default=True,
        ),
    ]
