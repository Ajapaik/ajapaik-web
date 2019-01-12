# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0037_auto_20151127_1458'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 27, 13, 6, 16, 395604, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='video',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 27, 13, 6, 20, 620555, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
