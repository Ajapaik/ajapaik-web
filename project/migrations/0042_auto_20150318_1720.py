# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0041_catphoto_source_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='cattagphoto',
            name='album',
            field=models.ForeignKey(default=1, to='project.CatAlbum'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cattag',
            name='name',
            field=models.CharField(unique=True, max_length=255),
            preserve_default=True,
        ),
    ]
