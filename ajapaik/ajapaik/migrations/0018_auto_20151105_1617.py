# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0017_auto_20151105_1603'),
    ]

    operations = [
        migrations.AddField(
            model_name='dating',
            name='raw',
            field=models.CharField(default='asd', max_length=25),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='dating',
            name='end_accuracy',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(0, 'Day'), (1, 'Month'), (2, 'Year')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dating',
            name='start_accuracy',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(0, 'Day'), (1, 'Month'), (2, 'Year')]),
            preserve_default=True,
        ),
    ]
