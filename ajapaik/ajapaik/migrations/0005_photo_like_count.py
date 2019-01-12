# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0004_photolike'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='like_count',
            field=models.IntegerField(default=0, db_index=True),
            preserve_default=True,
        ),
    ]
