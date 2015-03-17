# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0033_auto_20150317_1628'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CatTagPhoto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.PositiveSmallIntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('photo', models.ForeignKey(to='project.CatPhoto')),
                ('tag', models.ForeignKey(to='project.CatTag')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='catphoto',
            name='tags',
            field=models.ManyToManyField(related_name='photos', through='project.CatTagPhoto', to='project.CatTag'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='catalbum',
            name='photos',
            field=models.ManyToManyField(related_name='albums', to='project.CatPhoto'),
            preserve_default=True,
        ),
    ]
