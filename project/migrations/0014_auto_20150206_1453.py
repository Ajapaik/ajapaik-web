# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0013_geotag_hint_used'),
    ]

    operations = [
        migrations.AddField(
            model_name='area',
            name='name_se',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='photo',
            name='description_se',
            field=models.TextField(max_length=2047, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='photo',
            name='title_se',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
    ]
