# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0004_auto_20161010_1939'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flipfeedback',
            name='photo',
        ),
        migrations.RemoveField(
            model_name='flipfeedback',
            name='user_profile',
        ),
        migrations.RemoveField(
            model_name='photometadataupdate',
            name='photo',
        ),
        migrations.AlterUniqueTogether(
            name='photo',
            unique_together=set([('source', 'external_id', 'external_sub_id')]),
        ),
        migrations.DeleteModel(
            name='FlipFeedback',
        ),
        migrations.DeleteModel(
            name='PhotoMetadataUpdate',
        ),
        migrations.RemoveField(
            model_name='photo',
            name='image_no_watermark',
        ),
    ]
