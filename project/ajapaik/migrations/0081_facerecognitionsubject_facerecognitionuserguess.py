# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0080_auto_20181107_2124'),
    ]

    operations = [
        migrations.CreateModel(
            name='FaceRecognitionSubject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(to='ajapaik.Profile')),
            ],
            options={
                'db_table': 'project_face_recognition_subject',
            },
        ),
        migrations.CreateModel(
            name='FaceRecognitionUserGuess',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('coordinates', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('photo', models.ForeignKey(to='ajapaik.Photo')),
                ('subject', models.ForeignKey(to='ajapaik.FaceRecognitionSubject')),
                ('user', models.ForeignKey(to='ajapaik.Profile')),
            ],
            options={
                'db_table': 'project_face_recognition_user_guess',
            },
        ),
    ]
