# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0069_album_photo_count_with_subalbums'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='cover_photo',
            field=models.ForeignKey(blank=True, to='project.Photo', null=True),
            preserve_default=True,
        ),
    ]
