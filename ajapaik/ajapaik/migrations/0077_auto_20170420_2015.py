# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0076_auto_20170214_1741'),
    ]

    operations = [
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
            model_name='album',
            name='videos',
            field=models.ManyToManyField(related_name='albums', to='ajapaik.Video'),
        ),
        migrations.AlterField(
            model_name='albumphoto',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='albumphoto',
            name='type',
            field=models.PositiveSmallIntegerField(default=2, db_index=True, choices=[(0, b'Curated'), (1, b'Re-curated'), (2, b'Manual'), (3, b'Still'), (4, b'Uploaded')]),
        ),
        migrations.AlterField(
            model_name='credentialsmodel',
            name='id',
            field=models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, on_delete=models.deletion.CASCADE),
        ),
        migrations.AlterField(
            model_name='flowmodel',
            name='id',
            field=models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, on_delete=models.deletion.CASCADE),
        ),
        migrations.AlterField(
            model_name='geotag',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='points',
            name='action',
            field=models.PositiveSmallIntegerField(db_index=True, choices=[(0, 'Geot\xe4\xe4g'), (1, '\xdclepildistus'), (2, 'Foto \xfcleslaadimine'), (3, 'Foto kureerimine'), (4, 'Foto rekureerimine'), (5, 'Dateering'), (6, 'Dateeringu kinnitus'), (7, 'Filmikaader')]),
        ),
        migrations.AlterField(
            model_name='profile',
            name='deletion_attempted',
            field=models.DateTimeField(db_index=True, null=True, blank=True),
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
        migrations.AlterField(
            model_name='tour',
            name='photos',
            field=models.ManyToManyField(related_name='tours', to='ajapaik.Photo'),
        ),
        migrations.AlterField(
            model_name='tourgroup',
            name='members',
            field=models.ManyToManyField(related_name='tour_groups', to='ajapaik.Profile'),
        ),
    ]
