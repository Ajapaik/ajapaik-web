# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0037_auto_20150317_1821'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cattag',
            name='left_child',
        ),
        migrations.RemoveField(
            model_name='cattag',
            name='right_child',
        ),
        migrations.AddField(
            model_name='cattag',
            name='level',
            field=models.SmallIntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
