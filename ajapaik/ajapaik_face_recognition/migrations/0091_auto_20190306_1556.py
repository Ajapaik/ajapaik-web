# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik_face_recognition', '0090_facerecognitionrectangle_face_encoding'),
    ]

    operations = [
        migrations.AddField(
            model_name='facerecognitionrectangle',
            name='origin',
            field=models.PositiveSmallIntegerField(default=1, choices=[(0, 'Kasutaja'), (1, 'Algorithm'), (2, 'Picasa')]),
        ),
        migrations.AddField(
            model_name='facerecognitionuserguess',
            name='origin',
            field=models.PositiveSmallIntegerField(default=1, choices=[(0, 'Kasutaja'), (1, 'Algorithm'), (2, 'Picasa')]),
        ),
    ]
