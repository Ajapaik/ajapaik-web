# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0003_auto_20150924_1651'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhotoLike',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level', models.PositiveSmallIntegerField(default=1)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('photo', models.ForeignKey(related_name='likes', to='ajapaik.Photo')),
                ('profile', models.ForeignKey(to='ajapaik.Profile')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
