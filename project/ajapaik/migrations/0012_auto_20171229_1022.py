# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_comments_xtd', '0004_auto_20170221_1510'),
        ('ajapaik', '0011_auto_20170308_1322'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyXtdComment',
            fields=[
                ('xtdcomment_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='django_comments_xtd.XtdComment')),
                ('facebook_comment_id', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
                'ordering': ('submit_date',),
                'abstract': False,
                'verbose_name': 'comment',
                'verbose_name_plural': 'comments',
                'permissions': [('can_moderate', 'Can moderate comments')],
            },
            bases=('django_comments_xtd.xtdcomment',),
        ),
        migrations.RemoveField(
            model_name='photo',
            name='fb_comments_count',
        ),
        migrations.AddField(
            model_name='geotag',
            name='photo_flipped',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='photo',
            name='comment_count',
            field=models.IntegerField(default=0, null=True, db_index=True, blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='deletion_attempted',
            field=models.DateTimeField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='lat',
            field=models.FloatField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='lon',
            field=models.FloatField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='albumphoto',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='albumphoto',
            name='type',
            field=models.PositiveSmallIntegerField(default=2, db_index=True, choices=[(0, b'Curated'), (1, b'Re-curated'), (2, b'Manual'), (4, b'Uploaded')]),
        ),
        migrations.AlterField(
            model_name='geotag',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='first_comment',
            field=models.DateTimeField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='first_dating',
            field=models.DateTimeField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='first_geotag',
            field=models.DateTimeField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='first_like',
            field=models.DateTimeField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='first_rephoto',
            field=models.DateTimeField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='latest_comment',
            field=models.DateTimeField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='latest_dating',
            field=models.DateTimeField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='latest_geotag',
            field=models.DateTimeField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='latest_like',
            field=models.DateTimeField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='latest_rephoto',
            field=models.DateTimeField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='points',
            name='action',
            field=models.PositiveSmallIntegerField(db_index=True, choices=[(0, 'Geotag'), (1, 'Refoto'), (2, 'Opplasting av foto'), (3, 'Utvalg av foto'), (4, 'Foto re-kuratering'), (5, 'Datering'), (6, 'Bekreftelse av datering'), (7, 'Stillbilde')]),
        ),
        migrations.AlterField(
            model_name='profile',
            name='fb_email',
            field=models.CharField(db_index=True, max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='fb_id',
            field=models.CharField(db_index=True, max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='google_plus_email',
            field=models.CharField(db_index=True, max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='google_plus_id',
            field=models.CharField(db_index=True, max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='score',
            field=models.PositiveIntegerField(default=0, db_index=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='score_recent_activity',
            field=models.PositiveIntegerField(default=0, db_index=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='score_rephoto',
            field=models.PositiveIntegerField(default=0, db_index=True),
        ),
    ]
