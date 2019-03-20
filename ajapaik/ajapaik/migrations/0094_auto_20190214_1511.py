# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0093_auto_20190214_1328'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='photo',
            name='perceptual_hash_0',
        ),
        migrations.RemoveField(
            model_name='photo',
            name='perceptual_hash_1',
        ),
        migrations.RemoveField(
            model_name='photo',
            name='perceptual_hash_2',
        ),
        migrations.RemoveField(
            model_name='photo',
            name='perceptual_hash_3',
        ),
        migrations.RemoveField(
            model_name='photo',
            name='perceptual_hash_4',
        ),
        migrations.RemoveField(
            model_name='photo',
            name='perceptual_hash_5',
        ),
        migrations.RemoveField(
            model_name='photo',
            name='perceptual_hash_6',
        ),
        migrations.RemoveField(
            model_name='photo',
            name='perceptual_hash_7',
        ),
        migrations.AddField(
            model_name='photo',
            name='perceptual_hash',
            field=models.CharField(max_length=64, blank=True, null=True),
        ),
    ]
