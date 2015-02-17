# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0017_auto_20150210_1556'),
    ]

    operations = [
        migrations.CreateModel(
            name='Licence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('url', models.TextField(null=True, blank=True)),
                ('image_url', models.TextField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
