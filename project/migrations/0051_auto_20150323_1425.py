# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0050_catphoto_source_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catphoto',
            name='source_url',
            field=models.URLField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
    ]
