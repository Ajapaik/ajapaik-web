# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0009_auto_20150121_1213'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='score_last_1000_geotags',
            new_name='score_recent_activity',
        ),
    ]
