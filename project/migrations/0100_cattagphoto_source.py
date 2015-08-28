# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0099_remove_catrealtag_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='cattagphoto',
            name='source',
            field=models.CharField(default=b'mob', max_length=3),
            preserve_default=True,
        ),
    ]
