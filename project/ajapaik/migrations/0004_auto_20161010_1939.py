# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0003_auto_20161008_2308'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='photo',
            unique_together=set([('source', 'source_key')]),
        ),
    ]
