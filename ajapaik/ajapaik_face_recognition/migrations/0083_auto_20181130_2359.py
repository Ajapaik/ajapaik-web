# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik_face_recognition', '0082_auto_20181121_2300'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='facerecognitionrectangle',
            name='is_rejected',
        ),
        migrations.AlterField(
            model_name='facerecognitionuserguess',
            name='user',
            field=models.ForeignKey(related_name='face_recognition_guesses', blank=True, to='ajapaik.Profile', null=True),
        ),
    ]
