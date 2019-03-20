# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0089_photo_perceptual_hash'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='similar_photos',
            field=models.ManyToManyField(blank=True, null=True, related_name='_photo_similar_photos_+', to='ajapaik.Photo'),
        ),
    ]
