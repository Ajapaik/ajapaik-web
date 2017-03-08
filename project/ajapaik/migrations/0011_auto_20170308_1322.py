# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0010_auto_20170117_1524'),
    ]

    operations = [
        migrations.AlterField(
            model_name='licence',
            name='name',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='licence',
            name='name_en',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='licence',
            name='name_no',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
