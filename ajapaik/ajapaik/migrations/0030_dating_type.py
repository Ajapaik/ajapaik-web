# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0029_dating_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='dating',
            name='type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Regular'), (1, 'Kinnitus')]),
            preserve_default=True,
        ),
    ]
