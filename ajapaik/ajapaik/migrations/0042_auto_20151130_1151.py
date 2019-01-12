# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0041_auto_20151130_1149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='videos',
            field=models.ManyToManyField(related_name='albums', null=True, to='ajapaik.Video', blank=True),
            preserve_default=True,
        ),
    ]
