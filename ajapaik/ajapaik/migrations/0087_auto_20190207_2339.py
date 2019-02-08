# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0086_photo_face_detection_attempted_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='album',
            old_name='face_encoding',
            new_name='face_encodings',
        ),
    ]
