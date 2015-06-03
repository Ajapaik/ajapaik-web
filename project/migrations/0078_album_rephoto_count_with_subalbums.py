# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0077_auto_20150528_1748'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='rephoto_count_with_subalbums',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
