# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0059_profile_send_then_and_now_photos_to_ajapaik'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='is_then_and_now_rephoto',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
