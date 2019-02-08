# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0020_auto_20151105_1843'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tour',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'thenandnow_tour',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TourPhoto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('photo', models.ForeignKey(to='ajapaik.Photo')),
                ('tour', models.ForeignKey(to='ajapaik.Tour')),
            ],
            options={
                'db_table': 'thenandnow_tourphoto',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='tour',
            name='photos',
            field=models.ManyToManyField(related_name='tours', through='ajapaik.TourPhoto', to='ajapaik.Photo'),
            preserve_default=True,
        ),
    ]
