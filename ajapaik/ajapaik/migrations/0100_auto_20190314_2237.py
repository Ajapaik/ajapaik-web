# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0099_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='confirmed_similar_photo_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='album',
            name='similar_photo_count',
            field=models.IntegerField(default=0),
        ),
    ]
