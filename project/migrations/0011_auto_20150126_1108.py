# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0010_auto_20150121_1600'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='skip',
            options={'verbose_name': 'Skip', 'verbose_name_plural': 'Skips'},
        ),
    ]
