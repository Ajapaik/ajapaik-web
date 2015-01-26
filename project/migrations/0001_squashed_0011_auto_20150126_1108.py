# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import oauth2client.django_orm
from django.conf import settings
import django.contrib.gis.db.models.fields
import project.home.models
import django_extensions.db.fields.json


class Migration(migrations.Migration):

    replaces = [(b'project', '0001_initial'), (b'project', '0002_photo_geography'), (b'project', '0003_geotag_origin'), (b'project', '0004_auto_20150106_1449'), (b'project', '0005_auto_20150106_1450'), (b'project', '0006_auto_20150106_1451'), (b'project', '0007_auto_20150116_1526'), (b'project', '0008_points'), (b'project', '0009_auto_20150121_1213'), (b'project', '0010_auto_20150121_1600'), (b'project', '0011_auto_20150126_1108')]

    dependencies = [
        ('auth', '0001_initial'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=255)),
                ('related_id', models.PositiveIntegerField(null=True, blank=True)),
                ('params', django_extensions.db.fields.json.JSONField(null=True, blank=True)),
                ('related_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField()),
                ('description', models.TextField(null=True, blank=True)),
                ('atype', models.PositiveSmallIntegerField(choices=[(0, b'Frontpage'), (1, b'Favorites'), (2, b'Collection')])),
                ('is_public', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AlbumPhoto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort_order', models.PositiveSmallIntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('album', models.ForeignKey(to='project.Album')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('lat', models.FloatField(null=True)),
                ('lon', models.FloatField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CredentialsModel',
            fields=[
                ('id', models.ForeignKey(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('credential', oauth2client.django_orm.CredentialsField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('camera_make', models.CharField(max_length=255, null=True, blank=True)),
                ('camera_model', models.CharField(max_length=255, null=True, blank=True)),
                ('lens_make', models.CharField(max_length=255, null=True, blank=True)),
                ('lens_model', models.CharField(max_length=255, null=True, blank=True)),
                ('software', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DifficultyFeedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level', models.PositiveSmallIntegerField()),
                ('trustworthiness', models.FloatField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FlipFeedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('flip', models.NullBooleanField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FlowModel',
            fields=[
                ('id', models.ForeignKey(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('flow', oauth2client.django_orm.FlowField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GeoTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lat', models.FloatField()),
                ('lon', models.FloatField()),
                ('azimuth', models.FloatField(null=True, blank=True)),
                ('azimuth_line_end_lat', models.FloatField(null=True, blank=True)),
                ('azimuth_line_end_lon', models.FloatField(null=True, blank=True)),
                ('zoom_level', models.IntegerField(null=True, blank=True)),
                ('type', models.PositiveSmallIntegerField(choices=[(0, b'Map'), (1, b'EXIF'), (2, b'GPS')])),
                ('is_correct', models.NullBooleanField()),
                ('score', models.PositiveSmallIntegerField()),
                ('azimuth_score', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('trustworthiness', models.FloatField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('image', models.ImageField(null=True, upload_to=project.home.models.PathAndRename(b'/uploads'), blank=True)),
                ('image_unscaled', models.ImageField(null=True, upload_to=project.home.models.PathAndRename(b'/uploads'), blank=True)),
                ('flip', models.NullBooleanField()),
                ('date', models.DateField(null=True, blank=True)),
                ('date_text', models.CharField(max_length=100, null=True, blank=True)),
                ('description', models.TextField(max_length=2047, null=True, blank=True)),
                ('level', models.PositiveSmallIntegerField(default=0)),
                ('guess_level', models.FloatField(null=True, blank=True)),
                ('lat', models.FloatField(null=True, blank=True)),
                ('lon', models.FloatField(null=True, blank=True)),
                ('bounding_circle_radius', models.FloatField(null=True, blank=True)),
                ('azimuth', models.FloatField(null=True, blank=True)),
                ('confidence', models.FloatField(default=0)),
                ('azimuth_confidence', models.FloatField(default=0)),
                ('source_key', models.CharField(max_length=100, null=True, blank=True)),
                ('source_url', models.URLField(max_length=1023, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('cam_scale_factor', models.FloatField(null=True, blank=True)),
                ('cam_yaw', models.FloatField(null=True, blank=True)),
                ('cam_pitch', models.FloatField(null=True, blank=True)),
                ('cam_roll', models.FloatField(null=True, blank=True)),
                ('city', models.ForeignKey(related_name='cities', to='project.City')),
                ('device', models.ForeignKey(blank=True, to='project.Device', null=True)),
                ('rephoto_of', models.ForeignKey(related_name='rephotos', blank=True, to='project.Photo', null=True)),
            ],
            options={
                'ordering': ['-id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('fb_name', models.CharField(max_length=255, null=True, blank=True)),
                ('fb_link', models.CharField(max_length=255, null=True, blank=True)),
                ('fb_id', models.CharField(max_length=100, null=True, blank=True)),
                ('fb_token', models.CharField(max_length=511, null=True, blank=True)),
                ('fb_hometown', models.CharField(max_length=511, null=True, blank=True)),
                ('fb_current_location', models.CharField(max_length=511, null=True, blank=True)),
                ('fb_birthday', models.DateField(null=True, blank=True)),
                ('fb_email', models.CharField(max_length=255, null=True, blank=True)),
                ('fb_user_friends', models.TextField(null=True, blank=True)),
                ('google_plus_id', models.CharField(max_length=100, null=True, blank=True)),
                ('google_plus_link', models.CharField(max_length=255, null=True, blank=True)),
                ('google_plus_name', models.CharField(max_length=255, null=True, blank=True)),
                ('google_plus_token', models.CharField(max_length=255, null=True, blank=True)),
                ('google_plus_picture', models.CharField(max_length=255, null=True, blank=True)),
                ('avatar_url', models.URLField(null=True, blank=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('score', models.PositiveIntegerField(default=0)),
                ('score_rephoto', models.PositiveIntegerField(default=0)),
                ('score_last_1000_geotags', models.PositiveIntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Skip',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('photo', models.ForeignKey(to='project.Photo')),
                ('user', models.ForeignKey(related_name='skips', to='project.Profile')),
            ],
            options={
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
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserMapView',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('confidence', models.FloatField(default=0)),
                ('action', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('photo', models.ForeignKey(to='project.Photo')),
                ('user_profile', models.ForeignKey(to='project.Profile')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='photo',
            name='source',
            field=models.ForeignKey(blank=True, to='project.Source', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='photo',
            name='user',
            field=models.ForeignKey(related_name='photos', blank=True, to='project.Profile', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='geotag',
            name='photo',
            field=models.ForeignKey(related_name='geotags', to='project.Photo'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='geotag',
            name='user',
            field=models.ForeignKey(related_name='geotags', to='project.Profile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='flipfeedback',
            name='photo',
            field=models.ForeignKey(to='project.Photo'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='flipfeedback',
            name='user_profile',
            field=models.ForeignKey(to='project.Profile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='difficultyfeedback',
            name='geotag',
            field=models.ForeignKey(to='project.GeoTag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='difficultyfeedback',
            name='photo',
            field=models.ForeignKey(to='project.Photo'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='difficultyfeedback',
            name='user_profile',
            field=models.ForeignKey(to='project.Profile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='albumphoto',
            name='photo',
            field=models.ForeignKey(to='project.Photo'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='album',
            name='photos',
            field=models.ManyToManyField(related_name='albums', through='project.AlbumPhoto', to=b'project.Photo'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='album',
            name='profile',
            field=models.ForeignKey(related_name='albums', blank=True, to='project.Profile', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='CSVPhoto',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('project.photo',),
        ),
        migrations.AddField(
            model_name='photo',
            name='geography',
            field=django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, geography=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='geotag',
            name='origin',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, b'Game'), (1, b'Map'), (2, b'Grid')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=models.ImageField(null=True, upload_to=b'/uploads', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=models.ImageField(null=True, upload_to=b'%Y/%m/%d', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=models.ImageField(null=True, upload_to=project.home.models.PathAndRename(b'uploads'), blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='image_unscaled',
            field=models.ImageField(null=True, upload_to=project.home.models.PathAndRename(b'uploads'), blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='date',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Points',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action', models.PositiveSmallIntegerField(choices=[(0, b'Geotag'), (1, b'Rephoto')])),
                ('action_reference', models.PositiveIntegerField()),
                ('points', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('created', models.DateTimeField(db_index=True)),
                ('user', models.ForeignKey(related_name='points', to='project.Profile')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RenameField(
            model_name='profile',
            old_name='score_last_1000_geotags',
            new_name='score_recent_activity',
        ),
        migrations.AlterModelOptions(
            name='skip',
            options={'verbose_name': 'Skip', 'verbose_name_plural': 'Skips'},
        ),
    ]
