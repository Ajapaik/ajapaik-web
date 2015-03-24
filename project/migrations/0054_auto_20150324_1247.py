# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0053_album_geography'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatUserFavorite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('album', models.ForeignKey(to='project.CatAlbum')),
                ('photo', models.ForeignKey(to='project.CatPhoto')),
                ('profile', models.ForeignKey(to='project.Profile')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='geotag',
            name='type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Kaart'), (1, 'EXIF'), (2, 'GPS')]),
            preserve_default=True,
        ),
    ]
