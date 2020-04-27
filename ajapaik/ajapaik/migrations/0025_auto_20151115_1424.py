# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0024_auto_20151115_1233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tourphoto',
            name='photo',
            field=models.ForeignKey(related_name='tour_photos', to='ajapaik.Photo', on_delete=models.deletion.CASCADE),
            preserve_default=True,
        ),
    ]
