# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='points',
            name='album',
            field=models.ForeignKey(blank=True, to='ajapaik.Album', null=True, on_delete=models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='points',
            name='action',
            field=models.PositiveSmallIntegerField(choices=[(0, b'Geotag'), (1, b'Rephoto'), (2, b'Photo upload'), (3, b'Photo curation'), (4, b'Photo re-curation')]),
            preserve_default=True,
        ),
    ]
