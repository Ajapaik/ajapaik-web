# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0061_catpushdevice_service_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='catpushdevice',
            old_name='push_token',
            new_name='token',
        ),
        migrations.RenameField(
            model_name='catpushdevice',
            old_name='service_type',
            new_name='type',
        ),
    ]
