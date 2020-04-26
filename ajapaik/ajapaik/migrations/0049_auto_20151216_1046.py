# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0048_tour_ordered'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tour',
            name='user_lat',
        ),
        migrations.RemoveField(
            model_name='tour',
            name='user_lng',
        ),
        migrations.AlterField(
            model_name='tourrephoto',
            name='original',
            field=models.ForeignKey(related_name='tour_rephotos', to='ajapaik.Photo', on_delete=models.deletion.CASCADE),
            preserve_default=True,
        ),
    ]
