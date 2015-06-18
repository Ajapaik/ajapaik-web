# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0087_auto_20150618_1151'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='rotated',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
