# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0047_auto_20150320_1831'),
    ]

    operations = [
        migrations.AddField(
            model_name='cattag',
            name='active',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
