# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0068_photo_fb_comments_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='photo_count_with_subalbums',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
