# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0014_dating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dating',
            name='end',
            field=models.DateField(default=datetime.date(3000, 1, 1), null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dating',
            name='start',
            field=models.DateField(default=datetime.date(1000, 1, 1), null=True, blank=True),
            preserve_default=True,
        ),
    ]
