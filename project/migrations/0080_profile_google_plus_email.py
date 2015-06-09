# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0079_auto_20150608_1610'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='google_plus_email',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
    ]
