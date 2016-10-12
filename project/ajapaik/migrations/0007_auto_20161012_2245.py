# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0006_auto_20161010_2036'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='send_then_and_now_photos_to_ajapaik',
        ),
        migrations.AlterField(
            model_name='photo',
            name='country',
            field=models.ForeignKey(related_name='photos', blank=True, to='ajapaik.Country', null=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='county',
            field=models.ForeignKey(related_name='photos', blank=True, to='ajapaik.County', null=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='municipality',
            field=models.ForeignKey(related_name='photos', blank=True, to='ajapaik.Municipality', null=True),
        ),
    ]
