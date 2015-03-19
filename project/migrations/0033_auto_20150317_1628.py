# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import project.home.models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0032_auto_20150312_1251'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatAlbum',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('subtitle', models.CharField(max_length=255)),
                ('image', models.ImageField(max_length=255, upload_to=project.home.models.PathAndRename(b'cat'))),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CatPhoto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(null=True, blank=True)),
                ('image', models.ImageField(max_length=255, upload_to=project.home.models.PathAndRename(b'cat'))),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='catalbum',
            name='photos',
            field=models.ManyToManyField(to='project.CatPhoto'),
            preserve_default=True,
        ),
    ]
