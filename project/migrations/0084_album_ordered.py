# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0083_auto_20150610_1218'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='ordered',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
