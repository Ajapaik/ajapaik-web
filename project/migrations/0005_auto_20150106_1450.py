# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0004_auto_20150106_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=models.ImageField(null=True, upload_to=b'%Y/%m/%d', blank=True),
            preserve_default=True,
        ),
    ]
