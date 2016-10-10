# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0005_auto_20161010_2016'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='photo',
            unique_together=set([('source', 'external_id')]),
        ),
    ]
