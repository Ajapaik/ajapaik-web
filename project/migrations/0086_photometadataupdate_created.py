# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0085_photometadataupdate'),
    ]

    operations = [
        migrations.AddField(
            model_name='photometadataupdate',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 17, 11, 48, 46, 737519, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
