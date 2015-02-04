# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0008_auto_20150202_1637'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='City',
            new_name='Area',
        ),
        migrations.RemoveField(
            model_name='album',
            name='geography',
        ),
        migrations.RemoveField(
            model_name='album',
            name='lat',
        ),
        migrations.RemoveField(
            model_name='album',
            name='lon',
        ),
        migrations.RemoveField(
            model_name='photo',
            name='city',
        ),
        migrations.AddField(
            model_name='photo',
            name='area',
            field=models.ForeignKey(related_name='areas', blank=True, to='project.Area', null=True),
            preserve_default=True,
        ),
    ]
