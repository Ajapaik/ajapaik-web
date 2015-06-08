# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0078_album_rephoto_count_with_subalbums'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='comments_count_with_subalbums',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='album',
            name='geotagged_photo_count_with_subalbums',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
