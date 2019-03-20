# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0094_auto_20190214_1511'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='confirmed_similar_photos',
            field=models.ManyToManyField(blank=True, related_name='_photo_confirmed_similar_photos_+', to='ajapaik.Photo'),
        ),
    ]
