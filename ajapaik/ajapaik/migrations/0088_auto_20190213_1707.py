# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0087_auto_20190207_2339'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='similar_photos',
            field=models.ManyToManyField(related_name='_photo_similar_photos_+', to='ajapaik.Photo'),
        ),
    ]
