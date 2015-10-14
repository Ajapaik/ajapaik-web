# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sift', '0004_catphoto_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catphoto',
            name='slug',
            field=autoslug.fields.AutoSlugField(always_update=True, populate_from=b'title', editable=False),
            preserve_default=True,
        ),
    ]
