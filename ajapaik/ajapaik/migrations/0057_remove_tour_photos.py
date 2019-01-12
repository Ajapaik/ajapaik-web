# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0056_auto_20151218_1201'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tour',
            name='photos',
        ),
    ]
