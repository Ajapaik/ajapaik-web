# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0015_auto_20150206_1458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='guess_level',
            field=models.FloatField(default=3),
            preserve_default=True,
        ),
    ]
