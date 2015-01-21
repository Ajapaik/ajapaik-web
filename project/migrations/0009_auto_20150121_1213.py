# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0008_points'),
    ]

    operations = [
        migrations.AlterField(
            model_name='points',
            name='created',
            field=models.DateTimeField(db_index=True),
            preserve_default=True,
        ),
    ]
