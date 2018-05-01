# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0081_create_social_network_accounts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='difficultyfeedback',
            name='user_profile',
            field=models.ForeignKey(related_name='difficulty_feedbacks', blank=True, to='ajapaik.Profile', null=True),
        ),
    ]
