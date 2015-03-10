# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0026_auto_20150304_1626'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='atype',
            field=models.PositiveSmallIntegerField(choices=[(0, b'Curated'), (1, b'Favorites'), (2, b'Auto')]),
            preserve_default=True,
        ),
    ]
