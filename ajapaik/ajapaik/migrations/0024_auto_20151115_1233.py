# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0023_auto_20151114_2302'),
    ]

    operations = [
        migrations.AddField(
            model_name='tour',
            name='user',
            field=models.ForeignKey(default=1, to='ajapaik.Profile', on_delete=models.deletion.CASCADE),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tourrephoto',
            name='original',
            field=models.ForeignKey(default=1, to='ajapaik.Photo', on_delete=models.deletion.CASCADE),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tourrephoto',
            name='tour',
            field=models.ForeignKey(default=1, to='ajapaik.Tour', on_delete=models.deletion.CASCADE),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tourrephoto',
            name='user',
            field=models.ForeignKey(default=1, to='ajapaik.Profile', on_delete=models.deletion.CASCADE),
            preserve_default=False,
        ),
    ]
