# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik_face_recognition', '0086_auto_20181211_2312'),
    ]

    operations = [
        migrations.AddField(
            model_name='facerecognitionsubject',
            name='is_public_figure',
            field=models.BooleanField(default=False),
        ),
    ]
