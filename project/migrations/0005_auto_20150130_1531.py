# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0004_auto_20150130_1158'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='city',
            field=models.ForeignKey(related_name='cities', blank=True, to='project.City', null=True),
            preserve_default=True,
        ),
    ]
