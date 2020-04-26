# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0061_auto_20160107_1617'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='photo',
            name='is_then_and_now_rephoto',
        ),
        migrations.AddField(
            model_name='photo',
            name='then_and_now_rephoto',
            field=models.ForeignKey(blank=True, to='ajapaik.TourRephoto', null=True, on_delete=models.deletion.CASCADE),
            preserve_default=True,
        ),
    ]
