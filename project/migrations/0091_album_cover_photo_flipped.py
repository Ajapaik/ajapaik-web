# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0090_auto_20150707_1800'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='cover_photo_flipped',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
