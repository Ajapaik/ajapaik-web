# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0028_album_is_public_mutable'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='subalbum_of',
            field=models.ForeignKey(related_name='subalbums', blank=True, to='project.Album', null=True),
            preserve_default=True,
        ),
    ]
