# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0058_auto_20151218_1202'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='send_then_and_now_photos_to_ajapaik',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
