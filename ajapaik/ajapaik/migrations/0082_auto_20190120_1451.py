# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('ajapaik', '0081_auto_20190119_0038'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='album',
            name='face_encoding',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='album',
            name='gender',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(1, 'Female'), (0, 'Male')]),
        ),
        migrations.AddField(
            model_name='album',
            name='is_public_figure',
            field=models.BooleanField(default=False),
        ),
    ]
