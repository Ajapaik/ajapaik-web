# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields.json


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0093_auto_20150819_1421'),
    ]

    operations = [
        migrations.AlterField(
            model_name='googlemapsreversegeocode',
            name='response',
            field=django_extensions.db.fields.json.JSONField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='licence',
            name='image_url',
            field=models.URLField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='licence',
            name='url',
            field=models.URLField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
