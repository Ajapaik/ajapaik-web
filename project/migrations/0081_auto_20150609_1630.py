# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0080_profile_google_plus_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='google_plus_token',
            field=models.CharField(max_length=511, null=True, blank=True),
            preserve_default=True,
        ),
    ]
