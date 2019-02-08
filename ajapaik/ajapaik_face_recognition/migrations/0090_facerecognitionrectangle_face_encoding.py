# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik_face_recognition', '0089_auto_20190123_2328'),
    ]

    operations = [
        migrations.AddField(
            model_name='facerecognitionrectangle',
            name='face_encoding',
            field=models.TextField(blank=True, null=True),
        ),
    ]
