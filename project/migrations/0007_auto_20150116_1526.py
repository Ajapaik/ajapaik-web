# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0006_auto_20150106_1451'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='date',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
