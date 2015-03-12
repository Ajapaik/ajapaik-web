# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0031_auto_20150311_1536'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='lat',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='album',
            name='lon',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='album',
            name='description',
            field=models.TextField(max_length=2047, null=True, blank=True),
            preserve_default=True,
        ),
    ]
