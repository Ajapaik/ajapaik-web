# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0031_auto_20151118_1804'),
    ]

    operations = [
        migrations.AddField(
            model_name='dating',
            name='confirmation_of',
            field=models.ForeignKey(related_name='confirmations', blank=True, to='ajapaik.Dating', null=True),
            preserve_default=True,
        ),
    ]
