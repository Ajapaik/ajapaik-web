# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0066_auto_20160426_1241'),
    ]

    operations = [
        migrations.CreateModel(
            name='NorwegianCSVPhoto',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('ajapaik.photo',),
        ),
    ]
