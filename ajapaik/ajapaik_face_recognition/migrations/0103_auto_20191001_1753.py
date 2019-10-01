# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-10-01 14:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik_face_recognition', '0102_auto_20190929_2012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facerecognitionrectangle',
            name='age',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(0, 'Child'), (1, 'Adult'), (2, 'Elderly'), (3, 'Tundmatu'), (4, 'Not Applicable')], null=True),
        ),
        migrations.AlterField(
            model_name='facerecognitionrectanglesubjectdataguess',
            name='age',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Child'), (1, 'Adult'), (2, 'Elderly'), (3, 'Tundmatu'), (4, 'Not Applicable')], null=True),
        ),
    ]
