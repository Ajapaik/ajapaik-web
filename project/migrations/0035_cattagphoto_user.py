# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0034_auto_20150317_1648'),
    ]

    operations = [
        migrations.AddField(
            model_name='cattagphoto',
            name='user',
            field=models.ForeignKey(default=18585, to='project.Profile'),
            preserve_default=False,
        ),
    ]
