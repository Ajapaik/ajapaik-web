# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0027_auto_20151115_1429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tourphoto',
            name='photo',
            field=models.ForeignKey(to='ajapaik.Photo'),
            preserve_default=True,
        ),
    ]
