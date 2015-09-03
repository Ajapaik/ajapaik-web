# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatAlbum',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('title_et', models.CharField(max_length=255, null=True)),
                ('title_en', models.CharField(max_length=255, null=True)),
                ('title_fi', models.CharField(max_length=255, null=True)),
                ('subtitle', models.CharField(max_length=255)),
                ('subtitle_et', models.CharField(max_length=255, null=True)),
                ('subtitle_en', models.CharField(max_length=255, null=True)),
                ('subtitle_fi', models.CharField(max_length=255, null=True)),
                ('image', models.ImageField(max_length=255, upload_to=b'cat')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'project_catalbum',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CatAppliedTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'db_table': 'project_catappliedtag',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CatPhoto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(null=True, blank=True)),
                ('height', models.IntegerField(null=True, blank=True)),
                ('width', models.IntegerField(null=True, blank=True)),
                ('image', models.ImageField(height_field=b'height', width_field=b'width', max_length=255, upload_to=b'cat')),
                ('author', models.CharField(max_length=255, null=True, blank=True)),
                ('source_url', models.URLField(max_length=255, null=True, blank=True)),
                ('source_key', models.CharField(max_length=255, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'project_catphoto',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CatProfile',
            fields=[
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'project_catprofile',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CatPushDevice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=254)),
                ('token', models.CharField(max_length=254)),
                ('filter', models.CharField(max_length=1000, null=True, blank=True)),
                ('profile', models.ForeignKey(to='sift.CatProfile')),
            ],
            options={
                'db_table': 'project_catpushdevice',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CatRealTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
            options={
                'db_table': 'project_catrealtag',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CatTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('level', models.SmallIntegerField(null=True, blank=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'project_cattag',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CatTagPhoto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.IntegerField(db_index=True)),
                ('source', models.CharField(default=b'mob', max_length=3)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('album', models.ForeignKey(to='sift.CatAlbum')),
                ('photo', models.ForeignKey(to='sift.CatPhoto')),
                ('profile', models.ForeignKey(related_name='tags', to='sift.CatProfile')),
                ('tag', models.ForeignKey(to='sift.CatTag')),
            ],
            options={
                'db_table': 'project_cattagphoto',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CatUserFavorite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('album', models.ForeignKey(to='sift.CatAlbum')),
                ('photo', models.ForeignKey(to='sift.CatPhoto')),
                ('profile', models.ForeignKey(to='sift.CatProfile')),
            ],
            options={
                'db_table': 'project_catuserfavorite',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
                'db_table': 'project_source',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='catuserfavorite',
            unique_together=set([('album', 'photo', 'profile')]),
        ),
        migrations.AddField(
            model_name='catphoto',
            name='source',
            field=models.ForeignKey(blank=True, to='sift.Source', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='catphoto',
            name='tags',
            field=models.ManyToManyField(related_name='photos', through='sift.CatTagPhoto', to='sift.CatTag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='catappliedtag',
            name='photo',
            field=models.ForeignKey(to='sift.CatPhoto'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='catappliedtag',
            name='tag',
            field=models.ForeignKey(to='sift.CatRealTag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='catalbum',
            name='photos',
            field=models.ManyToManyField(related_name='album', to='sift.CatPhoto'),
            preserve_default=True,
        ),
    ]
