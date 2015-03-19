# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0039_catphoto_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='catphoto',
            name='source',
            field=models.ForeignKey(blank=True, to='project.Source', null=True),
            preserve_default=True,
        ),
    ]
