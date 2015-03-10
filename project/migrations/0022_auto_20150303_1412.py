# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import project.home.models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0021_auto_20150303_1409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=models.ImageField(height_field=b'height', width_field=b'width', null=True, upload_to=project.home.models.PathAndRename(b'uploads'), blank=True),
            preserve_default=True,
        ),
    ]
