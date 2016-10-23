# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0007_auto_20161012_2245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='albumphoto',
            name='profile',
            field=models.ForeignKey(related_name='album_photo_links', blank=True, to='ajapaik.Profile', null=True),
        ),
        migrations.AlterField(
            model_name='difficultyfeedback',
            name='user_profile',
            field=models.ForeignKey(related_name='difficulty_feedbacks', to='ajapaik.Profile'),
        ),
    ]
