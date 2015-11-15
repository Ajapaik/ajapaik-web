# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0026_auto_20151115_1425'),
    ]

    operations = [
        migrations.AddField(
            model_name='tourrephoto',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 15, 12, 29, 12, 622687, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tourrephoto',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 15, 12, 29, 19, 576493, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
