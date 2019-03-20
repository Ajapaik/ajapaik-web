# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0091_auto_20190213_2353'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='photo',
            name='similar_photos',
        ),
    ]
