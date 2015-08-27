# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0097_catappliedtag'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatRealTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='catappliedtag',
            name='tag',
            field=models.ForeignKey(to='project.CatRealTag'),
            preserve_default=True,
        ),
    ]
