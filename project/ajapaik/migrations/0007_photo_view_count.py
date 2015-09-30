# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0006_auto_20150929_1805'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='view_count',
            field=models.PositiveIntegerField(default=0, db_index=True),
            preserve_default=True,
        ),
    ]
