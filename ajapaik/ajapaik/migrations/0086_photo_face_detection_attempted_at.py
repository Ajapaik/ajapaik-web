# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0085_auto_20190207_0227'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='face_detection_attempted_at',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
    ]
