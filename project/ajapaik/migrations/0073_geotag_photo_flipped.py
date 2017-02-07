# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0072_profile_deletion_attempted'),
    ]

    operations = [
        migrations.AddField(
            model_name='geotag',
            name='photo_flipped',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
