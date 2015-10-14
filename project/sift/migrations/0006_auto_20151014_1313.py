# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sift', '0005_auto_20151014_1211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catappliedtag',
            name='photo',
            field=models.ForeignKey(related_name='applied_tags', to='sift.CatPhoto'),
            preserve_default=True,
        ),
    ]
