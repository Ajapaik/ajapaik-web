# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0057_remove_tour_photos'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tour',
            name='photos1',
        ),
        migrations.AddField(
            model_name='tour',
            name='photos',
            field=models.ManyToManyField(related_name='tours', null=True, to='ajapaik.Photo', blank=True),
            preserve_default=True,
        ),
    ]
