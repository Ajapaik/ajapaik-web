# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0097_auto_20190312_1904'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='confirmed_similar_photo_count_with_subalbums',
            field=models.IntegerField(default=7),
        ),
        migrations.AlterField(
            model_name='album',
            name='similar_photo_count_with_subalbums',
            field=models.IntegerField(default=5),
        ),
    ]
