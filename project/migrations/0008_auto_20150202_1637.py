# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0007_auto_20150202_1517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='atype',
            field=models.PositiveSmallIntegerField(choices=[(0, b'Frontpage'), (1, b'Favorites'), (2, b'Collection')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='album',
            name='slug',
            field=models.SlugField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
