# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0095_auto_20150825_1737'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cattagphoto',
            name='value',
            field=models.IntegerField(db_index=True),
            preserve_default=True,
        ),
    ]
