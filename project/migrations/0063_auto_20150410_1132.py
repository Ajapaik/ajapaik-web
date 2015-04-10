# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0062_auto_20150409_1605'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cattagphoto',
            name='profile',
            field=models.ForeignKey(related_name='tags', to='project.Profile'),
            preserve_default=True,
        ),
    ]
