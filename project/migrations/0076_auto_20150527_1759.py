# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0075_photocomment'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='fb_object_id',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='photocomment',
            name='fb_object_id',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
