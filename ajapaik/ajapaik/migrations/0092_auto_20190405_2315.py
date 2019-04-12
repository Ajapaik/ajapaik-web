# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-05 20:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0091_migrate_old_users_to_allauth'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='credentialsmodel',
            name='id',
        ),
        migrations.RemoveField(
            model_name='flowmodel',
            name='id',
        ),
        migrations.AddField(
            model_name='album',
            name='confirmed_similar_photo_count_with_subalbums',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='album',
            name='similar_photo_count_with_subalbums',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='photo',
            name='confirmed_similar_photos',
            field=models.ManyToManyField(blank=True, related_name='_photo_confirmed_similar_photos_+', to='ajapaik.Photo'),
        ),
        migrations.AddField(
            model_name='photo',
            name='perceptual_hash',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='similar_photos',
            field=models.ManyToManyField(blank=True, related_name='_photo_similar_photos_+', to='ajapaik.Photo'),
        ),
        migrations.DeleteModel(
            name='CredentialsModel',
        ),
        migrations.DeleteModel(
            name='FlowModel',
        ),
    ]