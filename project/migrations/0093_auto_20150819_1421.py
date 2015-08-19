# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0092_auto_20150819_1406'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoogleMapsReverseGeocode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lat', models.FloatField(db_index=True, validators=[django.core.validators.MinValueValidator(-85.05115), django.core.validators.MaxValueValidator(85)])),
                ('lon', models.FloatField(db_index=True, validators=[django.core.validators.MinValueValidator(-180), django.core.validators.MaxValueValidator(180)])),
                ('response', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='licence',
            name='image_url',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
    ]
