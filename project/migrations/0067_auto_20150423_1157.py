# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0066_auto_20150420_1131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=models.ImageField(upload_to=b'uploads', width_field=b'width', height_field=b'height', max_length=255, blank=True, null=True),
            preserve_default=True,
        ),
    ]
