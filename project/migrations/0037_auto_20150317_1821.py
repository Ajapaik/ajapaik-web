# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0036_auto_20150317_1751'),
    ]

    operations = [
        migrations.AddField(
            model_name='cattag',
            name='left_child',
            field=models.ForeignKey(related_name='left_parent', blank=True, to='project.CatTag', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cattag',
            name='right_child',
            field=models.ForeignKey(related_name='right_parent', blank=True, to='project.CatTag', null=True),
            preserve_default=True,
        ),
    ]
