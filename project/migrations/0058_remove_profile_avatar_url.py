# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0057_auto_20150331_1457'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='avatar_url',
        ),
    ]
