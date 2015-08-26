# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0094_auto_20150819_1428'),
    ]

    operations = [
        migrations.AddField(
            model_name='catphoto',
            name='height',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='catphoto',
            name='width',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='catphoto',
            name='image',
            field=models.ImageField(height_field=b'height', width_field=b'width', max_length=255, upload_to=b'cat'),
            preserve_default=True,
        ),
    ]
