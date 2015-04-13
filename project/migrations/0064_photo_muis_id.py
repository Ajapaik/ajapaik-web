# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0063_auto_20150410_1132'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='muis_id',
            field=models.CharField(max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
    ]
