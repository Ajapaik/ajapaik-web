# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik_face_recognition', '0083_auto_20181130_2359'),
    ]

    operations = [
        migrations.AddField(
            model_name='facerecognitionrectangle',
            name='subject_consensus',
            field=models.ForeignKey(blank=True, to='ajapaik_face_recognition.FaceRecognitionSubject', null=True, on_delete=models.deletion.CASCADE),
        ),
    ]
