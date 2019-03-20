# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0092_remove_photo_similar_photos'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='photo',
            name='perceptual_hash',
        ),
        migrations.AddField(
            model_name='photo',
            name='perceptual_hash_0',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='perceptual_hash_1',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='perceptual_hash_2',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='perceptual_hash_3',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='perceptual_hash_4',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='perceptual_hash_5',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='perceptual_hash_6',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='perceptual_hash_7',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='similar_photos',
            field=models.ManyToManyField(blank=True, related_name='_photo_similar_photos_+', to='ajapaik.Photo'),
        ),
    ]
