# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0088_auto_20190305_2203'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='wikidata_qid',
            field=models.CharField(verbose_name='Wikidata identifier', max_length=255, blank=True, null=True),
        ),
    ]
