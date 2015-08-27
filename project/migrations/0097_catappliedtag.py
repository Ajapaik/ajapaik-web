# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0096_auto_20150826_1755'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatAppliedTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('photo', models.ForeignKey(to='project.CatPhoto')),
                ('tag', models.ForeignKey(to='project.CatTag')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
