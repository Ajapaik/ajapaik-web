# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0047_photo_image_no_watermark'),
    ]

    operations = [
        migrations.AddField(
            model_name='tour',
            name='ordered',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
