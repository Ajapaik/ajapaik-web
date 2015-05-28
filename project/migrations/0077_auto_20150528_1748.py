# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0076_auto_20150527_1759'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photocomment',
            name='photo',
            field=models.ForeignKey(related_name='comments', to='project.Photo'),
            preserve_default=True,
        ),
    ]
