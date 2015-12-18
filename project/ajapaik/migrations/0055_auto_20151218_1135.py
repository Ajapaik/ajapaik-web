# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0054_auto_20151217_1204'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tour',
            name='members',
        ),
        migrations.AlterField(
            model_name='tour',
            name='photos',
            field=models.ManyToManyField(related_name='tours', null=True, through='ajapaik.TourPhoto', to='ajapaik.Photo', blank=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='tourgroup',
            unique_together=set([('name', 'tour')]),
        ),
    ]
