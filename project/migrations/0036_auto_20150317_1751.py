# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0035_cattagphoto_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cattagphoto',
            old_name='user',
            new_name='profile',
        ),
    ]
