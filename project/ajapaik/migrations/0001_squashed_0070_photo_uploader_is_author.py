# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc
import django.contrib.gis.db.models.fields
import django_extensions.db.fields.json
import oauth2client.django_orm
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    replaces = [(b'ajapaik', '0001_initial'), (b'ajapaik', '0002_auto_20150924_1300'), (b'ajapaik', '0003_auto_20150924_1651'), (b'ajapaik', '0004_photolike'), (b'ajapaik', '0005_photo_like_count'), (b'ajapaik', '0006_auto_20150929_1805'), (b'ajapaik', '0007_photo_view_count'), (b'ajapaik', '0008_auto_20150930_1512'), (b'ajapaik', '0009_auto_20151022_1253'), (b'ajapaik', '0010_photo_keywords'), (b'ajapaik', '0011_newsletter'), (b'ajapaik', '0012_auto_20151029_1745'), (b'ajapaik', '0013_auto_20151102_1708'), (b'ajapaik', '0014_dating'), (b'ajapaik', '0015_auto_20151105_1130'), (b'ajapaik', '0016_auto_20151105_1131'), (b'ajapaik', '0017_auto_20151105_1603'), (b'ajapaik', '0018_auto_20151105_1617'), (b'ajapaik', '0019_auto_20151105_1831'), (b'ajapaik', '0020_auto_20151105_1843'), (b'ajapaik', '0021_auto_20151114_1421'), (b'ajapaik', '0022_tourrephoto'), (b'ajapaik', '0023_auto_20151114_2302'), (b'ajapaik', '0024_auto_20151115_1233'), (b'ajapaik', '0025_auto_20151115_1424'), (b'ajapaik', '0026_auto_20151115_1425'), (b'ajapaik', '0027_auto_20151115_1429'), (b'ajapaik', '0028_auto_20151115_1559'), (b'ajapaik', '0029_dating_comment'), (b'ajapaik', '0030_dating_type'), (b'ajapaik', '0031_auto_20151118_1804'), (b'ajapaik', '0032_dating_confirmation_of'), (b'ajapaik', '0033_auto_20151119_1620'), (b'ajapaik', '0034_auto_20151120_1436'), (b'ajapaik', '0035_auto_20151125_1557'), (b'ajapaik', '0036_auto_20151127_1437'), (b'ajapaik', '0037_auto_20151127_1458'), (b'ajapaik', '0038_auto_20151127_1506'), (b'ajapaik', '0039_video_slug'), (b'ajapaik', '0040_auto_20151127_1537'), (b'ajapaik', '0041_auto_20151130_1149'), (b'ajapaik', '0042_auto_20151130_1151'), (b'ajapaik', '0043_auto_20151202_1216'), (b'ajapaik', '0044_auto_20151202_1754'), (b'ajapaik', '0045_video_date'), (b'ajapaik', '0046_auto_20151203_1629'), (b'ajapaik', '0047_photo_image_no_watermark'), (b'ajapaik', '0048_tour_ordered'), (b'ajapaik', '0049_auto_20151216_1046'), (b'ajapaik', '0050_auto_20151216_1125'), (b'ajapaik', '0051_tour_photo_set_type'), (b'ajapaik', '0052_auto_20151216_1536'), (b'ajapaik', '0053_auto_20151217_1157'), (b'ajapaik', '0054_auto_20151217_1204'), (b'ajapaik', '0055_auto_20151218_1135'), (b'ajapaik', '0056_auto_20151218_1201'), (b'ajapaik', '0057_remove_tour_photos'), (b'ajapaik', '0058_auto_20151218_1202'), (b'ajapaik', '0059_profile_send_then_and_now_photos_to_ajapaik'), (b'ajapaik', '0060_photo_is_then_and_now_rephoto'), (b'ajapaik', '0061_auto_20160107_1617'), (b'ajapaik', '0062_auto_20160107_1639'), (b'ajapaik', '0063_tour_description'), (b'ajapaik', '0064_auto_20160111_1203'), (b'ajapaik', '0065_auto_20160115_1521'), (b'ajapaik', '0066_auto_20160426_1241'), (b'ajapaik', '0067_norwegiancsvphoto'), (b'ajapaik', '0068_auto_20160509_1541'), (b'ajapaik', '0069_auto_20160509_1601'), (b'ajapaik', '0070_photo_uploader_is_author')]

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
                ('params', django_extensions.db.fields.json.JSONField(default=dict, null=True, blank=True)),
                ('related_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'db_table': 'project_action',
            },
        ),
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('name_et', models.CharField(max_length=255, null=True)),
                ('name_en', models.CharField(max_length=255, null=True)),
                ('name_ru', models.CharField(max_length=255, null=True)),
                ('name_fi', models.CharField(max_length=255, null=True)),
                ('name_sv', models.CharField(max_length=255, null=True)),
                ('name_nl', models.CharField(max_length=255, null=True)),
                ('name_de', models.CharField(max_length=255, null=True)),
                ('slug', models.SlugField(max_length=255, null=True, blank=True)),
                ('description', models.TextField(max_length=2047, null=True, blank=True)),
                ('atype', models.PositiveSmallIntegerField(choices=[(0, b'Curated'), (1, b'Favorites'), (2, b'Auto')])),
                ('is_public', models.BooleanField(default=True)),
                ('open', models.BooleanField(default=False)),
                ('ordered', models.BooleanField(default=False)),
                ('lat', models.FloatField(null=True, blank=True)),
                ('lon', models.FloatField(null=True, blank=True)),
                ('geography', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, geography=True, blank=True)),
                ('cover_photo_flipped', models.BooleanField(default=False)),
                ('photo_count_with_subalbums', models.IntegerField(default=0)),
                ('rephoto_count_with_subalbums', models.IntegerField(default=0)),
                ('geotagged_photo_count_with_subalbums', models.IntegerField(default=0)),
                ('comments_count_with_subalbums', models.IntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'project_album',
            },
        ),
        migrations.CreateModel(
            name='AlbumPhoto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('album', models.ForeignKey(to='ajapaik.Album')),
            ],
            options={
                'db_table': 'project_albumphoto',
            },
        ),
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('name_et', models.CharField(max_length=255, null=True)),
                ('name_en', models.CharField(max_length=255, null=True)),
                ('name_ru', models.CharField(max_length=255, null=True)),
                ('name_fi', models.CharField(max_length=255, null=True)),
                ('name_sv', models.CharField(max_length=255, null=True)),
                ('name_nl', models.CharField(max_length=255, null=True)),
                ('name_de', models.CharField(max_length=255, null=True)),
                ('lat', models.FloatField(null=True)),
                ('lon', models.FloatField(null=True)),
            ],
            options={
                'db_table': 'project_area',
            },
        ),
        migrations.CreateModel(
            name='CredentialsModel',
            fields=[
                ('id', models.ForeignKey(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('credential', oauth2client.django_orm.CredentialsField(null=True)),
            ],
            options={
                'db_table': 'project_credentialsmodel',
            },
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
                'db_table': 'project_device',
            },
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
                'db_table': 'project_difficultyfeedback',
            },
        ),
        migrations.CreateModel(
            name='FlipFeedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('flip', models.NullBooleanField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'project_flipfeedback',
            },
        ),
        migrations.CreateModel(
            name='FlowModel',
            fields=[
                ('id', models.ForeignKey(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('flow', oauth2client.django_orm.FlowField(null=True)),
            ],
            options={
                'db_table': 'project_flowmodel',
            },
        ),
        migrations.CreateModel(
            name='GeoTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lat', models.FloatField(validators=[django.core.validators.MinValueValidator(-85.05115), django.core.validators.MaxValueValidator(85)])),
                ('lon', models.FloatField(validators=[django.core.validators.MinValueValidator(-180), django.core.validators.MaxValueValidator(180)])),
                ('geography', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, geography=True, blank=True)),
                ('azimuth', models.FloatField(null=True, blank=True)),
                ('azimuth_line_end_lat', models.FloatField(null=True, blank=True)),
                ('azimuth_line_end_lon', models.FloatField(null=True, blank=True)),
                ('zoom_level', models.IntegerField(null=True, blank=True)),
                ('origin', models.PositiveSmallIntegerField(default=0, choices=[(0, 'M\xe4ng'), (1, 'Kaardivaade'), (2, 'Galerii')])),
                ('type', models.PositiveSmallIntegerField(default=0, choices=[(0, 'Kaart'), (1, 'EXIF'), (2, 'GPS'), (3, 'Kinnitus')])),
                ('map_type', models.PositiveSmallIntegerField(default=0, choices=[(0, 'Google kaart'), (1, 'Google satelliit'), (2, 'OpenStreetMap')])),
                ('hint_used', models.BooleanField(default=False)),
                ('is_correct', models.BooleanField(default=False)),
                ('azimuth_correct', models.BooleanField(default=False)),
                ('score', models.IntegerField(null=True, blank=True)),
                ('azimuth_score', models.IntegerField(null=True, blank=True)),
                ('trustworthiness', models.FloatField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'project_geotag',
            },
        ),
        migrations.CreateModel(
            name='GoogleMapsReverseGeocode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lat', models.FloatField(db_index=True, validators=[django.core.validators.MinValueValidator(-85.05115), django.core.validators.MaxValueValidator(85)])),
                ('lon', models.FloatField(db_index=True, validators=[django.core.validators.MinValueValidator(-180), django.core.validators.MaxValueValidator(180)])),
                ('response', django_extensions.db.fields.json.JSONField(default=dict)),
            ],
            options={
                'db_table': 'project_googlemapsreversegeocode',
            },
        ),
        migrations.CreateModel(
            name='Licence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('url', models.URLField(null=True, blank=True)),
                ('image_url', models.URLField(null=True, blank=True)),
            ],
            options={
                'db_table': 'project_licence',
            },
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=b'uploads', width_field=b'width', height_field=b'height', max_length=255, blank=True, null=True)),
                ('image_unscaled', models.ImageField(max_length=255, null=True, upload_to=b'uploads', blank=True)),
                ('height', models.IntegerField(null=True, blank=True)),
                ('width', models.IntegerField(null=True, blank=True)),
                ('flip', models.NullBooleanField()),
                ('invert', models.NullBooleanField()),
                ('stereo', models.NullBooleanField()),
                ('rotated', models.IntegerField(null=True, blank=True)),
                ('date', models.DateTimeField(null=True, blank=True)),
                ('date_text', models.CharField(max_length=255, null=True, blank=True)),
                ('title', models.CharField(max_length=255, null=True, blank=True)),
                ('title_et', models.CharField(max_length=255, null=True, blank=True)),
                ('title_en', models.CharField(max_length=255, null=True, blank=True)),
                ('title_ru', models.CharField(max_length=255, null=True, blank=True)),
                ('title_fi', models.CharField(max_length=255, null=True, blank=True)),
                ('title_sv', models.CharField(max_length=255, null=True, blank=True)),
                ('title_nl', models.CharField(max_length=255, null=True, blank=True)),
                ('title_de', models.CharField(max_length=255, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('description_et', models.TextField(null=True, blank=True)),
                ('description_en', models.TextField(null=True, blank=True)),
                ('description_ru', models.TextField(null=True, blank=True)),
                ('description_fi', models.TextField(null=True, blank=True)),
                ('description_sv', models.TextField(null=True, blank=True)),
                ('description_nl', models.TextField(null=True, blank=True)),
                ('description_de', models.TextField(null=True, blank=True)),
                ('author', models.CharField(max_length=255, null=True, blank=True)),
                ('types', models.CharField(max_length=255, null=True, blank=True)),
                ('level', models.PositiveSmallIntegerField(default=0)),
                ('guess_level', models.FloatField(default=3)),
                ('lat', models.FloatField(blank=True, null=True, db_index=True, validators=[django.core.validators.MinValueValidator(-85.05115), django.core.validators.MaxValueValidator(85)])),
                ('lon', models.FloatField(blank=True, null=True, db_index=True, validators=[django.core.validators.MinValueValidator(-180), django.core.validators.MaxValueValidator(180)])),
                ('geography', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, geography=True, blank=True)),
                ('bounding_circle_radius', models.FloatField(null=True, blank=True)),
                ('address', models.CharField(max_length=255, null=True, blank=True)),
                ('azimuth', models.FloatField(null=True, blank=True)),
                ('confidence', models.FloatField(default=0, null=True, blank=True)),
                ('azimuth_confidence', models.FloatField(default=0, null=True, blank=True)),
                ('source_key', models.CharField(max_length=100, null=True, blank=True)),
                ('muis_id', models.CharField(max_length=100, null=True, blank=True)),
                ('muis_media_id', models.CharField(max_length=100, null=True, blank=True)),
                ('source_url', models.URLField(max_length=1023, null=True, blank=True)),
                ('first_rephoto', models.DateTimeField(null=True, blank=True)),
                ('latest_rephoto', models.DateTimeField(null=True, blank=True)),
                ('fb_object_id', models.CharField(max_length=255, null=True, blank=True)),
                ('fb_comments_count', models.IntegerField(default=0)),
                ('first_comment', models.DateTimeField(null=True, blank=True)),
                ('latest_comment', models.DateTimeField(null=True, blank=True)),
                ('geotag_count', models.IntegerField(default=0, db_index=True)),
                ('first_geotag', models.DateTimeField(null=True, blank=True)),
                ('latest_geotag', models.DateTimeField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('gps_accuracy', models.FloatField(null=True, blank=True)),
                ('gps_fix_age', models.FloatField(null=True, blank=True)),
                ('cam_scale_factor', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.5), django.core.validators.MaxValueValidator(4.0)])),
                ('cam_yaw', models.FloatField(null=True, blank=True)),
                ('cam_pitch', models.FloatField(null=True, blank=True)),
                ('cam_roll', models.FloatField(null=True, blank=True)),
                ('area', models.ForeignKey(related_name='areas', blank=True, to='ajapaik.Area', null=True)),
                ('device', models.ForeignKey(blank=True, to='ajapaik.Device', null=True)),
                ('licence', models.ForeignKey(blank=True, to='ajapaik.Licence', null=True)),
                ('rephoto_of', models.ForeignKey(related_name='rephotos', blank=True, to='ajapaik.Photo', null=True)),
            ],
            options={
                'ordering': ['-id'],
                'db_table': 'project_photo',
            },
        ),
        migrations.CreateModel(
            name='PhotoComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fb_comment_id', models.CharField(unique=True, max_length=255)),
                ('fb_object_id', models.CharField(max_length=255)),
                ('fb_comment_parent_id', models.CharField(max_length=255, null=True, blank=True)),
                ('fb_user_id', models.CharField(max_length=255)),
                ('text', models.TextField()),
                ('created', models.DateTimeField()),
                ('photo', models.ForeignKey(related_name='comments', to='ajapaik.Photo')),
            ],
            options={
                'db_table': 'project_photocomment',
            },
        ),
        migrations.CreateModel(
            name='PhotoMetadataUpdate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('old_title', models.CharField(max_length=255, null=True, blank=True)),
                ('new_title', models.CharField(max_length=255, null=True, blank=True)),
                ('old_description', models.TextField(null=True, blank=True)),
                ('new_description', models.TextField(null=True, blank=True)),
                ('old_author', models.CharField(max_length=255, null=True, blank=True)),
                ('new_author', models.CharField(max_length=255, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('photo', models.ForeignKey(related_name='metadata_updates', to='ajapaik.Photo')),
            ],
            options={
                'db_table': 'project_photometadataupdate',
            },
        ),
        migrations.CreateModel(
            name='Points',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action', models.PositiveSmallIntegerField(choices=[(0, b'Geotag'), (1, b'Rephoto'), (2, b'Photo upload'), (3, b'Photo curation')])),
                ('points', models.IntegerField(default=0)),
                ('created', models.DateTimeField(db_index=True)),
                ('geotag', models.ForeignKey(blank=True, to='ajapaik.GeoTag', null=True)),
                ('photo', models.ForeignKey(blank=True, to='ajapaik.Photo', null=True)),
            ],
            options={
                'db_table': 'project_points',
                'verbose_name_plural': 'Points',
            },
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
                ('google_plus_email', models.CharField(max_length=255, null=True, blank=True)),
                ('google_plus_link', models.CharField(max_length=255, null=True, blank=True)),
                ('google_plus_name', models.CharField(max_length=255, null=True, blank=True)),
                ('google_plus_token', models.TextField(null=True, blank=True)),
                ('google_plus_picture', models.CharField(max_length=255, null=True, blank=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('score', models.PositiveIntegerField(default=0)),
                ('score_rephoto', models.PositiveIntegerField(default=0)),
                ('score_recent_activity', models.PositiveIntegerField(default=0)),
            ],
            options={
                'db_table': 'project_profile',
            },
        ),
        migrations.CreateModel(
            name='Skip',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('photo', models.ForeignKey(to='ajapaik.Photo')),
                ('user', models.ForeignKey(related_name='skips', to='ajapaik.Profile')),
            ],
            options={
                'db_table': 'project_skip',
            },
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
        ),
        migrations.AddField(
            model_name='points',
            name='user',
            field=models.ForeignKey(related_name='points', to='ajapaik.Profile'),
        ),
        migrations.AlterUniqueTogether(
            name='points',
            unique_together=set([('user', 'geotag')]),
        ),
        migrations.AddField(
            model_name='photo',
            name='source',
            field=models.ForeignKey(blank=True, to='ajapaik.Source', null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='user',
            field=models.ForeignKey(related_name='photos', blank=True, to='ajapaik.Profile', null=True),
        ),
        migrations.AddField(
            model_name='geotag',
            name='photo',
            field=models.ForeignKey(related_name='geotags', to='ajapaik.Photo'),
        ),
        migrations.AddField(
            model_name='geotag',
            name='user',
            field=models.ForeignKey(related_name='geotags', blank=True, to='ajapaik.Profile', null=True),
        ),
        migrations.AddField(
            model_name='flipfeedback',
            name='photo',
            field=models.ForeignKey(to='ajapaik.Photo'),
        ),
        migrations.AddField(
            model_name='flipfeedback',
            name='user_profile',
            field=models.ForeignKey(to='ajapaik.Profile'),
        ),
        migrations.AddField(
            model_name='difficultyfeedback',
            name='geotag',
            field=models.ForeignKey(to='ajapaik.GeoTag'),
        ),
        migrations.AddField(
            model_name='difficultyfeedback',
            name='photo',
            field=models.ForeignKey(to='ajapaik.Photo'),
        ),
        migrations.AddField(
            model_name='difficultyfeedback',
            name='user_profile',
            field=models.ForeignKey(to='ajapaik.Profile'),
        ),
        migrations.AddField(
            model_name='albumphoto',
            name='photo',
            field=models.ForeignKey(to='ajapaik.Photo'),
        ),
        migrations.AddField(
            model_name='album',
            name='cover_photo',
            field=models.ForeignKey(blank=True, to='ajapaik.Photo', null=True),
        ),
        migrations.AddField(
            model_name='album',
            name='photos',
            field=models.ManyToManyField(related_name='albums', through='ajapaik.AlbumPhoto', to=b'ajapaik.Photo'),
        ),
        migrations.AddField(
            model_name='album',
            name='profile',
            field=models.ForeignKey(related_name='albums', blank=True, to='ajapaik.Profile', null=True),
        ),
        migrations.AddField(
            model_name='album',
            name='subalbum_of',
            field=models.ForeignKey(related_name='subalbums', blank=True, to='ajapaik.Album', null=True),
        ),
        migrations.CreateModel(
            name='CSVPhoto',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('ajapaik.photo',),
        ),
        migrations.AddField(
            model_name='points',
            name='album',
            field=models.ForeignKey(blank=True, to='ajapaik.Album', null=True),
        ),
        migrations.AlterField(
            model_name='points',
            name='action',
            field=models.PositiveSmallIntegerField(choices=[(0, b'Geotag'), (1, b'Rephoto'), (2, b'Photo upload'), (3, b'Photo curation'), (4, b'Photo re-curation')]),
        ),
        migrations.AddField(
            model_name='albumphoto',
            name='profile',
            field=models.ForeignKey(blank=True, to='ajapaik.Profile', null=True),
        ),
        migrations.AddField(
            model_name='albumphoto',
            name='type',
            field=models.PositiveSmallIntegerField(default=2, choices=[(0, b'Curated'), (1, b'Re-curated'), (2, b'Manual'), (3, b'Still'), (4, b'Uploaded')]),
        ),
        migrations.CreateModel(
            name='PhotoLike',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level', models.PositiveSmallIntegerField(default=1)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('photo', models.ForeignKey(related_name='likes', to='ajapaik.Photo')),
                ('profile', models.ForeignKey(related_name='likes', to='ajapaik.Profile')),
            ],
        ),
        migrations.AddField(
            model_name='photo',
            name='like_count',
            field=models.IntegerField(default=0, db_index=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='first_like',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='latest_like',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='view_count',
            field=models.PositiveIntegerField(default=0, db_index=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='first_view',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='latest_view',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.RenameField(
            model_name='photo',
            old_name='muis_id',
            new_name='external_id',
        ),
        migrations.RenameField(
            model_name='photo',
            old_name='muis_media_id',
            new_name='external_sub_id',
        ),
        migrations.AlterField(
            model_name='geotag',
            name='origin',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'M\xe4ng'), (1, 'Kaardivaade'), (2, 'Gallery'), (3, 'Permalink')]),
        ),
        migrations.AddField(
            model_name='photo',
            name='keywords',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(unique=True, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'project_newsletter',
            },
        ),
        migrations.AlterField(
            model_name='geotag',
            name='type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Kaart'), (1, 'EXIF'), (2, 'GPS'), (3, 'Kinnitus'), (4, 'StreetView')]),
        ),
        migrations.AlterField(
            model_name='geotag',
            name='origin',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'M\xe4ng'), (1, 'Kaardivaade'), (2, 'Galerii'), (3, 'P\xfcsiviide')]),
        ),
        migrations.CreateModel(
            name='Dating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.DateField(default=datetime.date(1000, 1, 1))),
                ('start_approximate', models.BooleanField(default=False)),
                ('end', models.DateField(default=datetime.date(3000, 1, 1))),
                ('end_approximate', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('photo', models.ForeignKey(related_name='datings', to='ajapaik.Photo')),
                ('profile', models.ForeignKey(related_name='datings', to='ajapaik.Profile')),
                ('end_accuracy', models.PositiveSmallIntegerField(blank=True, null=True, choices=[(0, 'Day'), (1, 'Month'), (2, 'Year')])),
                ('start_accuracy', models.PositiveSmallIntegerField(blank=True, null=True, choices=[(0, 'Day'), (1, 'Month'), (2, 'Year')])),
                ('raw', models.CharField(max_length=25, null=True, blank=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('type', models.PositiveSmallIntegerField(default=0, choices=[(0, 'Regular'), (1, 'Kinnitus')])),
                ('confirmation_of', models.ForeignKey(related_name='confirmations', blank=True, to='ajapaik.Dating', null=True)),
            ],
            options={
                'db_table': 'project_dating',
            },
        ),
        migrations.AddField(
            model_name='points',
            name='dating',
            field=models.ForeignKey(blank=True, to='ajapaik.Dating', null=True),
        ),
        migrations.AlterField(
            model_name='points',
            name='action',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Geotag'), (1, '\xdclepildistus'), (2, 'Photo upload'), (3, 'Photo curation'), (4, 'Photo re-curation'), (5, 'Dating')]),
        ),
        migrations.AlterUniqueTogether(
            name='points',
            unique_together=set([('user', 'geotag'), ('user', 'dating')]),
        ),
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
        ),
        migrations.CreateModel(
            name='TourPhoto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(default=0)),
                ('photo', models.ForeignKey(to='ajapaik.Photo')),
                ('tour', models.ForeignKey(to='ajapaik.Tour')),
            ],
            options={
                'db_table': 'thenandnow_tourphoto',
            },
        ),
        migrations.AddField(
            model_name='tour',
            name='photos',
            field=models.ManyToManyField(related_name='tours', through='ajapaik.TourPhoto', to=b'ajapaik.Photo'),
        ),
        migrations.CreateModel(
            name='TourRephoto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(height_field=b'height', width_field=b'width', upload_to=b'then-and-now')),
                ('width', models.IntegerField(null=True, blank=True)),
                ('height', models.IntegerField(null=True, blank=True)),
                ('original', models.ForeignKey(default=1, to='ajapaik.Photo')),
            ],
            options={
                'db_table': 'thenandnow_tourrephoto',
            },
        ),
        migrations.AddField(
            model_name='tour',
            name='user',
            field=models.ForeignKey(default=1, to='ajapaik.Profile'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tourrephoto',
            name='tour',
            field=models.ForeignKey(related_name='tour_rephotos', to='ajapaik.Tour'),
        ),
        migrations.AddField(
            model_name='tourrephoto',
            name='user',
            field=models.ForeignKey(related_name='tour_rephotos', to='ajapaik.Profile'),
        ),
        migrations.AddField(
            model_name='tourrephoto',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 15, 12, 29, 12, 622687, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tourrephoto',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 15, 12, 29, 19, 576493, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='DatingConfirmation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('confirmation_of', models.ForeignKey(related_name='confirmations', to='ajapaik.Dating')),
                ('profile', models.ForeignKey(related_name='dating_confirmations', to='ajapaik.Profile')),
            ],
            options={
                'db_table': 'project_datingconfirmation',
            },
        ),
        migrations.RemoveField(
            model_name='dating',
            name='confirmation_of',
        ),
        migrations.RemoveField(
            model_name='dating',
            name='type',
        ),
        migrations.AddField(
            model_name='points',
            name='dating_confirmation',
            field=models.ForeignKey(blank=True, to='ajapaik.DatingConfirmation', null=True),
        ),
        migrations.AlterField(
            model_name='dating',
            name='end_accuracy',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(0, 'P\xe4ev'), (1, 'Kuu'), (2, 'Aasta')]),
        ),
        migrations.AlterField(
            model_name='dating',
            name='start_accuracy',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(0, 'P\xe4ev'), (1, 'Kuu'), (2, 'Aasta')]),
        ),
        migrations.AlterField(
            model_name='points',
            name='action',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Geot\xe4\xe4g'), (1, '\xdclepildistus'), (2, 'Foto \xfcleslaadimine'), (3, 'Foto kureerimine'), (4, 'Foto rekureerimine'), (5, 'Dateering'), (6, 'Dating confirmation')]),
        ),
        migrations.AlterUniqueTogether(
            name='points',
            unique_together=set([('user', 'dating_confirmation'), ('user', 'geotag'), ('user', 'dating')]),
        ),
        migrations.AddField(
            model_name='photo',
            name='dating_count',
            field=models.IntegerField(default=0, db_index=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='first_dating',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='latest_dating',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='points',
            name='action',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Geot\xe4\xe4g'), (1, '\xdclepildistus'), (2, 'Foto \xfcleslaadimine'), (3, 'Foto kureerimine'), (4, 'Foto rekureerimine'), (5, 'Dateering'), (6, 'Dateeringu kinnitus')]),
        ),
        migrations.AlterField(
            model_name='geotag',
            name='map_type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Google kaart'), (1, 'Google satelliit'), (2, 'OpenStreetMap'), (3, 'Juks')]),
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('file', models.FileField(null=True, upload_to=b'videos', blank=True)),
                ('cover_image', models.ImageField(height_field=b'cover_image_height', width_field=b'cover_image_width', null=True, upload_to=b'videos/covers', blank=True)),
                ('cover_image_height', models.IntegerField(null=True, blank=True)),
                ('cover_image_width', models.IntegerField(null=True, blank=True)),
                ('created', models.DateTimeField(default=datetime.datetime(2015, 11, 27, 13, 6, 16, 395604, tzinfo=utc), auto_now_add=True)),
                ('modified', models.DateTimeField(default=datetime.datetime(2015, 11, 27, 13, 6, 20, 620555, tzinfo=utc), auto_now=True)),
                ('slug', models.SlugField(max_length=255, unique=True, null=True, blank=True)),
                ('height', models.IntegerField(default=100)),
                ('width', models.IntegerField(default=100)),
                ('author', models.CharField(max_length=255, null=True, blank=True)),
                ('source', models.ForeignKey(blank=True, to='ajapaik.Source', null=True)),
                ('source_key', models.CharField(max_length=255, null=True, blank=True)),
                ('source_url', models.URLField(null=True, blank=True)),
                ('date', models.DateField(null=True, blank=True)),
            ],
            options={
                'db_table': 'project_video',
            },
        ),
        migrations.AddField(
            model_name='album',
            name='videos',
            field=models.ManyToManyField(related_name='albums', null=True, to=b'ajapaik.Video', blank=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='video',
            field=models.ForeignKey(related_name='stills', blank=True, to='ajapaik.Video', null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='video_timestamp',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='geotag',
            name='map_type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Google kaart'), (1, 'Google satelliit'), (2, 'OpenStreetMap'), (3, 'Juks'), (4, 'No map')]),
        ),
        migrations.AlterField(
            model_name='geotag',
            name='origin',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'M\xe4ng'), (1, 'Kaardivaade'), (2, 'Galerii'), (3, 'P\xfcsiviide'), (4, 'Source')]),
        ),
        migrations.AlterField(
            model_name='geotag',
            name='type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Kaart'), (1, 'EXIF'), (2, 'GPS'), (3, 'Kinnitus'), (4, 'StreetView'), (5, 'Source geotag')]),
        ),
        migrations.AddField(
            model_name='album',
            name='is_film_still_album',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='points',
            name='action',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Geot\xe4\xe4g'), (1, '\xdclepildistus'), (2, 'Foto \xfcleslaadimine'), (3, 'Foto kureerimine'), (4, 'Foto rekureerimine'), (5, 'Dateering'), (6, 'Dateeringu kinnitus'), (7, 'Film still')]),
        ),
        migrations.AlterField(
            model_name='geotag',
            name='map_type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Google kaart'), (1, 'Google satelliit'), (2, 'OpenStreetMap'), (3, 'Juks'), (4, 'Pole kaardilt')]),
        ),
        migrations.AlterField(
            model_name='geotag',
            name='origin',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'M\xe4ng'), (1, 'Kaardivaade'), (2, 'Galerii'), (3, 'P\xfcsiviide'), (4, 'Allikas')]),
        ),
        migrations.AlterField(
            model_name='geotag',
            name='type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Kaart'), (1, 'EXIF'), (2, 'GPS'), (3, 'Kinnitus'), (4, 'StreetView'), (5, 'Allika geot\xe4\xe4g')]),
        ),
        migrations.AlterField(
            model_name='points',
            name='action',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Geot\xe4\xe4g'), (1, '\xdclepildistus'), (2, 'Foto \xfcleslaadimine'), (3, 'Foto kureerimine'), (4, 'Foto rekureerimine'), (5, 'Dateering'), (6, 'Dateeringu kinnitus'), (7, 'Filmikaader')]),
        ),
        migrations.AddField(
            model_name='photo',
            name='image_no_watermark',
            field=models.ImageField(max_length=255, null=True, upload_to=b'uploads', blank=True),
        ),
        migrations.AddField(
            model_name='tour',
            name='ordered',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='tourrephoto',
            name='original',
            field=models.ForeignKey(related_name='tour_rephotos', to='ajapaik.Photo'),
        ),
        migrations.AddField(
            model_name='tour',
            name='photo_set_type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Fixed photo set'), (1, 'Any photos')]),
        ),
        migrations.CreateModel(
            name='TourGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=1, choices=[(b'A', b'A'), (b'B', b'B'), (b'C', b'C'), (b'D', b'D'), (b'E', b'E'), (b'F', b'F'), (b'G', b'G'), (b'H', b'H'), (b'I', b'I'), (b'J', b'J'), (b'K', b'K'), (b'L', b'L'), (b'M', b'M'), (b'N', b'N'), (b'O', b'O'), (b'P', b'P'), (b'Q', b'Q'), (b'R', b'R'), (b'S', b'S'), (b'T', b'T'), (b'U', b'U'), (b'V', b'V'), (b'W', b'W'), (b'X', b'X'), (b'Y', b'Y'), (b'Z', b'Z')])),
                ('max_members', models.IntegerField()),
                ('members', models.ManyToManyField(related_name='tour_groups', null=True, to=b'ajapaik.Profile', blank=True)),
                ('tour', models.ForeignKey(related_name='tour_groups', to='ajapaik.Tour')),
            ],
        ),
        migrations.AddField(
            model_name='tour',
            name='grouped',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='tour',
            name='user',
            field=models.ForeignKey(related_name='owned_tours', to='ajapaik.Profile'),
        ),
        migrations.AlterField(
            model_name='tour',
            name='photos',
            field=models.ManyToManyField(related_name='tours', null=True, through='ajapaik.TourPhoto', to=b'ajapaik.Photo', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='tourgroup',
            unique_together=set([('name', 'tour')]),
        ),
        migrations.CreateModel(
            name='TourPhotoOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(default=0)),
                ('photo', models.ForeignKey(to='ajapaik.Photo')),
                ('tour', models.ForeignKey(to='ajapaik.Tour')),
            ],
            options={
                'db_table': 'thenandnow_tourphotoorder',
            },
        ),
        migrations.RemoveField(
            model_name='tour',
            name='photos',
        ),
        migrations.AddField(
            model_name='tour',
            name='photos',
            field=models.ManyToManyField(related_name='tours', null=True, to=b'ajapaik.Photo', blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='send_then_and_now_photos_to_ajapaik',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='TourUniqueView',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('profile', models.ForeignKey(related_name='tour_views', to='ajapaik.Profile')),
                ('tour', models.ForeignKey(related_name='tour_views', to='ajapaik.Tour')),
            ],
            options={
                'db_table': 'thenandnow_touruniqueview',
            },
        ),
        migrations.AlterUniqueTogether(
            name='touruniqueview',
            unique_together=set([('tour', 'profile')]),
        ),
        migrations.AlterField(
            model_name='tour',
            name='photo_set_type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Valitud fotode tuur'), (1, 'Avatud pildivalik')]),
        ),
        migrations.AddField(
            model_name='photo',
            name='then_and_now_rephoto',
            field=models.ForeignKey(blank=True, to='ajapaik.TourRephoto', null=True),
        ),
        migrations.AddField(
            model_name='tour',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='tour',
            name='name',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='tour',
            name='photo_set_type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(1, 'Avatud tuur'), (0, 'Valitud fotode tuur'), (2, 'Tuur juhuslikult valitud piltidega Sinu l\xe4hikonnast')]),
        ),
        migrations.AddField(
            model_name='profile',
            name='first_name',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='last_name',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='album',
            name='name_no',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='area',
            name='name_no',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='description_no',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='title_no',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.CreateModel(
            name='NorwegianCSVPhoto',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('ajapaik.photo',),
        ),
        migrations.AddField(
            model_name='licence',
            name='name_de',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='licence',
            name='name_en',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='licence',
            name='name_et',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='licence',
            name='name_fi',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='licence',
            name='name_nl',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='licence',
            name='name_no',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='licence',
            name='name_ru',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='licence',
            name='name_sv',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='licence',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='photo',
            name='uploader_is_author',
            field=models.BooleanField(default=False),
        ),
    ]
