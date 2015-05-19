# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0067_auto_20150423_1157'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='fb_comments_count',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
