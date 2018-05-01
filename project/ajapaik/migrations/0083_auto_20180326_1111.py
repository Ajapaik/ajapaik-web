# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0082_auto_20180323_1625'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dating',
            name='profile',
            field=models.ForeignKey(related_name='datings', blank=True, to='ajapaik.Profile', null=True),
        ),
        migrations.AlterField(
            model_name='datingconfirmation',
            name='profile',
            field=models.ForeignKey(related_name='dating_confirmations', blank=True, to='ajapaik.Profile', null=True),
        ),
    ]
