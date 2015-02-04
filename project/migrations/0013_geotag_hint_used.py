# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0012_auto_20150204_1047'),
    ]

    operations = [
        migrations.AddField(
            model_name='geotag',
            name='hint_used',
            field=models.NullBooleanField(default=False),
            preserve_default=True,
        ),
    ]
