# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sift', '0002_auto_20151012_1516'),
    ]

    operations = [
        migrations.AddField(
            model_name='catphoto',
            name='flip',
            field=models.NullBooleanField(),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='catphoto',
            name='invert',
            field=models.NullBooleanField(),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='catphoto',
            name='rotated',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='catphoto',
            name='stereo',
            field=models.NullBooleanField(),
            preserve_default=True,
        ),
    ]
