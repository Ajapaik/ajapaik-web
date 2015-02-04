# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0011_auto_20150203_1648'),
    ]

    operations = [
        migrations.AlterField(
            model_name='points',
            name='action',
            field=models.PositiveSmallIntegerField(choices=[(0, b'Geotag'), (1, b'Rephoto'), (2, b'Photo upload')]),
            preserve_default=True,
        ),
    ]
