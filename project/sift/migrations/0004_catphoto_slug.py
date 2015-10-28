# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sift', '0003_auto_20151013_1404'),
    ]

    operations = [
        migrations.AddField(
            model_name='catphoto',
            name='slug',
            field=autoslug.fields.AutoSlugField(default='a', populate_from=b'title', editable=False),
            preserve_default=False,
        ),
    ]
