# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik_face_recognition', '0084_facerecognitionrectangle_subject_consensus'),
    ]

    operations = [
        migrations.AddField(
            model_name='facerecognitionsubject',
            name='face_encoding',
            field=models.TextField(null=True, blank=True),
        ),
    ]
