# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0071_auto_20161112_2228'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='deletion_attempted',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
