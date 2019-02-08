# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0074_auto_20170207_1830'),
    ]

    operations = [
        migrations.AddField(
            model_name='myxtdcomment',
            name='facebook_comment_id',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
    ]
