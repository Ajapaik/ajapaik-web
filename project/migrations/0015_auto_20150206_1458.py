# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0014_auto_20150206_1453'),
    ]

    operations = [
        migrations.RenameField(
            model_name='area',
            old_name='name_se',
            new_name='name_sv',
        ),
        migrations.RenameField(
            model_name='photo',
            old_name='description_se',
            new_name='description_sv',
        ),
        migrations.RenameField(
            model_name='photo',
            old_name='title_se',
            new_name='title_sv',
        ),
    ]
