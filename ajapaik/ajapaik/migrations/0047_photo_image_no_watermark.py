# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0046_auto_20151203_1629'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='image_no_watermark',
            field=models.ImageField(max_length=255, null=True, upload_to=b'uploads', blank=True),
            preserve_default=True,
        ),
    ]
