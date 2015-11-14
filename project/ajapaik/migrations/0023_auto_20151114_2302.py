# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0022_tourrephoto'),
    ]

    operations = [
        migrations.AddField(
            model_name='tour',
            name='user_lat',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(-85.05115), django.core.validators.MaxValueValidator(85)]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tour',
            name='user_lng',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(-180), django.core.validators.MaxValueValidator(180)]),
            preserve_default=True,
        ),
    ]
