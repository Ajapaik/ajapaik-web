# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0046_auto_20150320_1703'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cattagphoto',
            name='value',
            field=models.IntegerField(),
            preserve_default=True,
        ),
    ]
