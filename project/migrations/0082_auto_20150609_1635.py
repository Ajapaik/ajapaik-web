# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0081_auto_20150609_1630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='google_plus_token',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
