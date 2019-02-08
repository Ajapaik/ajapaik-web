# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0052_auto_20151216_1536'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tour',
            name='members',
            field=models.ManyToManyField(related_name='tours', null=True, to='ajapaik.Profile', blank=True),
            preserve_default=True,
        ),
    ]
