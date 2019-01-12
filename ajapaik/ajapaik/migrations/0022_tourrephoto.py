# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0021_auto_20151114_1421'),
    ]

    operations = [
        migrations.CreateModel(
            name='TourRephoto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(height_field=b'height', width_field=b'width', upload_to=b'then-and-now')),
                ('width', models.IntegerField(null=True, blank=True)),
                ('height', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'db_table': 'thenandnow_tourrephoto',
            },
            bases=(models.Model,),
        ),
    ]
