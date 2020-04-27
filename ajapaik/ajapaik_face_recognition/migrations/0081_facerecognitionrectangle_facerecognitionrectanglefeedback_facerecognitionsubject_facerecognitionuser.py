# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0080_auto_20181107_2124'),
    ]

    operations = [
        migrations.CreateModel(
            name='FaceRecognitionRectangle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_rejected', models.BooleanField(default=False)),
                ('coordinates', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('photo', models.ForeignKey(related_name='face_recognition_rectangles', to='ajapaik.Photo', on_delete=models.deletion.CASCADE)),
                ('user', models.ForeignKey(related_name='face_recognition_rectangles', blank=True, to='ajapaik.Profile', null=True, on_delete=models.deletion.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='FaceRecognitionRectangleFeedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_correct', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('rectangle', models.ForeignKey(related_name='feedback', to='ajapaik_face_recognition.FaceRecognitionRectangle', on_delete=models.deletion.CASCADE)),
                ('user', models.ForeignKey(related_name='face_recognition_rectangle_feedback', to='ajapaik.Profile', on_delete=models.deletion.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='FaceRecognitionSubject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('date_of_birth', models.DateField(null=True, blank=True)),
                ('gender', models.PositiveSmallIntegerField(blank=True, null=True, choices=[(1, 'Female'), (0, 'Male')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(to='ajapaik.Profile', on_delete=models.deletion.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='FaceRecognitionUserGuess',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('rectangle', models.ForeignKey(related_name='guesses', to='ajapaik_face_recognition.FaceRecognitionRectangle', on_delete=models.deletion.CASCADE)),
                ('subject', models.ForeignKey(related_name='guesses', to='ajapaik_face_recognition.FaceRecognitionSubject', on_delete=models.deletion.CASCADE)),
                ('user', models.ForeignKey(related_name='face_recognition_guesses', to='ajapaik.Profile', on_delete=models.deletion.CASCADE)),
            ],
        ),
    ]
