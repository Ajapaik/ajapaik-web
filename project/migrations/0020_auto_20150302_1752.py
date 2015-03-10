# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0019_auto_20150217_1507'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='height',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='photo',
            name='width',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
