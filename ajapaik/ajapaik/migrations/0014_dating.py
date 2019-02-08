# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0013_auto_20151102_1708'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.DateField(null=True, blank=True)),
                ('start_approximate', models.BooleanField(default=False)),
                ('end', models.DateField(null=True, blank=True)),
                ('end_approximate', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('photo', models.ForeignKey(related_name='datings', to='ajapaik.Photo')),
                ('profile', models.ForeignKey(related_name='datings', to='ajapaik.Profile')),
            ],
            options={
                'db_table': 'project_dating',
            },
            bases=(models.Model,),
        ),
    ]
