# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik_face_recognition', '0085_facerecognitionsubject_face_encoding'),
    ]

    operations = [
        migrations.AddField(
            model_name='facerecognitionrectangle',
            name='subject_ai_guess',
            field=models.ForeignKey(related_name='ai_detected_rectangles', blank=True, to='ajapaik_face_recognition.FaceRecognitionSubject', null=True),
        ),
        migrations.AlterField(
            model_name='facerecognitionrectangle',
            name='subject_consensus',
            field=models.ForeignKey(related_name='crowdsourced_rectangles', blank=True, to='ajapaik_face_recognition.FaceRecognitionSubject', null=True),
        ),
    ]
