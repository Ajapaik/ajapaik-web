# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0060_catpushdevice'),
    ]

    operations = [
        migrations.AddField(
            model_name='catpushdevice',
            name='service_type',
            field=models.CharField(default='gcm', max_length=254),
            preserve_default=False,
        ),
    ]
