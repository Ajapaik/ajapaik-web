# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0018_licence'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='licence',
            field=models.ForeignKey(blank=True, to='project.Licence', null=True),
            preserve_default=True,
        ),
    ]
