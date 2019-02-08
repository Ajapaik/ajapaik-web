# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik_face_recognition', '0088_auto_20190120_1451'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='facerecognitionsubject',
            name='photos',
        ),
        migrations.RemoveField(
            model_name='facerecognitionsubject',
            name='user',
        ),
        migrations.DeleteModel(
            name='FaceRecognitionSubject',
        ),
    ]
