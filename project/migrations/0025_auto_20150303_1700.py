# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0024_auto_20150303_1629'),
    ]

    operations = [
        migrations.AlterField(
            model_name='points',
            name='action_reference',
            field=models.PositiveIntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
