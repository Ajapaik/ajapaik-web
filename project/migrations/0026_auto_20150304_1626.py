# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0025_auto_20150303_1700'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='points',
            options={'verbose_name_plural': 'Points'},
        ),
        migrations.AddField(
            model_name='photo',
            name='invert',
            field=models.NullBooleanField(),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='photo',
            name='stereo',
            field=models.NullBooleanField(),
            preserve_default=True,
        ),
    ]
