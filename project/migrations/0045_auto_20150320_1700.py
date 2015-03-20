# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0044_geotag_azimuth_correct'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalbum',
            name='photos',
            field=models.ManyToManyField(related_name='albums', null=True, to='project.CatPhoto', blank=True),
            preserve_default=True,
        ),
    ]
