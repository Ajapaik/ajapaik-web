# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0009_auto_20151022_1253'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='keywords',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
