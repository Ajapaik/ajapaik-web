# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0073_auto_20150526_1505'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='geotag_count',
            field=models.IntegerField(default=0, db_index=True),
            preserve_default=True,
        ),
    ]
