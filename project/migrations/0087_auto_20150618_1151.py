# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0086_photometadataupdate_created'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='catphoto',
            unique_together=set([]),
        ),
    ]
