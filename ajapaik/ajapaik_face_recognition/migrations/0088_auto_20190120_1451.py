# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('ajapaik', '0082_auto_20190120_1451'),
        ('ajapaik_face_recognition', '0087_facerecognitionsubject_is_public_figure'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='facerecognitionuserguess',
            name='subject',
        ),
        migrations.AddField(
            model_name='facerecognitionuserguess',
            name='subject_album',
            field=models.ForeignKey(default=1, related_name='face_recognition_guesses', to='ajapaik.Album'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='facerecognitionrectangle',
            name='subject_ai_guess',
            field=models.ForeignKey(blank=True, null=True, related_name='face_recognition_ai_detected_rectangles',
                                    to='ajapaik.Album'),
        ),
        migrations.AlterField(
            model_name='facerecognitionrectangle',
            name='subject_consensus',
            field=models.ForeignKey(blank=True, null=True, related_name='face_recognition_crowdsourced_rectangles',
                                    to='ajapaik.Album'),
        ),
        migrations.AlterField(
            model_name='facerecognitionuserguess',
            name='rectangle',
            field=models.ForeignKey(related_name='face_recognition_guesses',
                                    to='ajapaik_face_recognition.FaceRecognitionRectangle'),
        ),
    ]
