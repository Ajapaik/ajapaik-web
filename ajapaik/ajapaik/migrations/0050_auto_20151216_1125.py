# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0049_auto_20151216_1046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tourrephoto',
            name='user',
            field=models.ForeignKey(related_name='tour_rephotos', to='ajapaik.Profile', on_delete=models.deletion.CASCADE),
            preserve_default=True,
        ),
    ]
