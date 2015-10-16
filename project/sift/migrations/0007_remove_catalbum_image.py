# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sift', '0006_auto_20151014_1313'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='catalbum',
            name='image',
        ),
    ]
