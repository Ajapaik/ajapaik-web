# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0020_auto_20150302_1752'),
    ]

    operations = [
        migrations.AddField(
            model_name='points',
            name='geotag',
            field=models.ForeignKey(blank=True, to='project.GeoTag', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='points',
            name='photo',
            field=models.ForeignKey(blank=True, to='project.Photo', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='points',
            name='action',
            field=models.PositiveSmallIntegerField(choices=[(0, b'Geotag'), (1, b'Rephoto'), (2, b'Photo upload'), (3, b'Photo curation')]),
            preserve_default=True,
        ),
    ]
