# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0053_auto_20151217_1157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tourgroup',
            name='members',
            field=models.ManyToManyField(related_name='tour_groups', null=True, to='ajapaik.Profile', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tourgroup',
            name='name',
            field=models.CharField(max_length=1, choices=[(b'A', b'A'), (b'B', b'B'), (b'C', b'C'), (b'D', b'D'), (b'E', b'E'), (b'F', b'F'), (b'G', b'G'), (b'H', b'H'), (b'I', b'I'), (b'J', b'J'), (b'K', b'K'), (b'L', b'L'), (b'M', b'M'), (b'N', b'N'), (b'O', b'O'), (b'P', b'P'), (b'Q', b'Q'), (b'R', b'R'), (b'S', b'S'), (b'T', b'T'), (b'U', b'U'), (b'V', b'V'), (b'W', b'W'), (b'X', b'X'), (b'Y', b'Y'), (b'Z', b'Z')]),
            preserve_default=True,
        ),
    ]
