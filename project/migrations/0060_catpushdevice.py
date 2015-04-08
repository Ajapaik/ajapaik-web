# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0059_auto_20150407_1450'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatPushDevice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('push_token', models.CharField(max_length=254)),
                ('filter', models.CharField(max_length=1000, null=True, blank=True)),
                ('profile', models.ForeignKey(to='project.Profile')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
