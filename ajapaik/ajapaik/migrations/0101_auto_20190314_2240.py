# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0100_auto_20190314_2237'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='album',
            name='confirmed_similar_photo_count',
        ),
        migrations.RemoveField(
            model_name='album',
            name='similar_photo_count',
        ),
    ]
