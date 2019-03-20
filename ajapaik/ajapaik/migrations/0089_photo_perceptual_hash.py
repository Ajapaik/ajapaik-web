# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0088_auto_20190213_1707'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='perceptual_hash',
            field=models.CharField(max_length=64, blank=True, null=True),
        ),
    ]
