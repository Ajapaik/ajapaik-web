# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0069_auto_20160509_1601'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='uploader_is_author',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
