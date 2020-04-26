# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0025_auto_20151115_1424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tourrephoto',
            name='tour',
            field=models.ForeignKey(related_name='tour_rephotos', to='ajapaik.Tour', on_delete=models.deletion.CASCADE),
            preserve_default=True,
        ),
    ]
