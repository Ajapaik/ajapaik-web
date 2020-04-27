# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik_face_recognition', '0081_facerecognitionrectangle_facerecognitionrectanglefeedback_facerecognitionsubject_facerecognitionuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='facerecognitionrectangle',
            name='deleted',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='facerecognitionsubject',
            name='photos',
            field=models.ManyToManyField(related_name='people', to='ajapaik.Photo, on_delete=models.deletion.CASCADE'),
        ),
    ]
