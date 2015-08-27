# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0098_auto_20150827_1523'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='catrealtag',
            name='active',
        ),
    ]
