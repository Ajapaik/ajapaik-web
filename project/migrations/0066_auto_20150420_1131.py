# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0065_auto_20150413_1704'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalbum',
            name='photos',
            field=models.ManyToManyField(related_name='album', to='project.CatPhoto'),
            preserve_default=True,
        ),
    ]
