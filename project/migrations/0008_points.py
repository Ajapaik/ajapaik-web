# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0007_auto_20150116_1526'),
    ]

    operations = [
        migrations.CreateModel(
            name='Points',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action', models.PositiveSmallIntegerField(choices=[(0, b'Geotag'), (1, b'Rephoto')])),
                ('action_reference', models.PositiveIntegerField()),
                ('points', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('user', models.ForeignKey(related_name='points', to='project.Profile')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
