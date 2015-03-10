# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0027_auto_20150305_1618'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='is_public_mutable',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
