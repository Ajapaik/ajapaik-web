# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0054_auto_20150324_1247'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='catuserfavorite',
            unique_together=set([('album', 'photo', 'profile')]),
        ),
    ]
