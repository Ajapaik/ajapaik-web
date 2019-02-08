# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0077_auto_20170420_2015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='videos',
            field=models.ManyToManyField(related_name='albums', null=True, to='ajapaik.Video', blank=True),
        ),
    ]
