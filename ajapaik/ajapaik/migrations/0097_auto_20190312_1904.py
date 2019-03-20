# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0096_auto_20190312_1856'),
    ]

    operations = [
        migrations.RenameField(
            model_name='album',
            old_name='confirmed_similar_photo_count',
            new_name='confirmed_similar_photo_count_with_subalbums',
        ),
        migrations.RenameField(
            model_name='album',
            old_name='similar_photo_count',
            new_name='similar_photo_count_with_subalbums',
        ),
    ]
