# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0070_photo_uploader_is_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='description',
            field=models.TextField(max_length=2047, null=True, verbose_name='Kirjeldus', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='album',
            name='is_public',
            field=models.BooleanField(default=True, verbose_name='On avalik'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='album',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Pealkiri'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='album',
            name='name_de',
            field=models.CharField(max_length=255, null=True, verbose_name='Pealkiri'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='album',
            name='name_en',
            field=models.CharField(max_length=255, null=True, verbose_name='Pealkiri'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='album',
            name='name_et',
            field=models.CharField(max_length=255, null=True, verbose_name='Pealkiri'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='album',
            name='name_fi',
            field=models.CharField(max_length=255, null=True, verbose_name='Pealkiri'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='album',
            name='name_nl',
            field=models.CharField(max_length=255, null=True, verbose_name='Pealkiri'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='album',
            name='name_no',
            field=models.CharField(max_length=255, null=True, verbose_name='Pealkiri'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='album',
            name='name_ru',
            field=models.CharField(max_length=255, null=True, verbose_name='Pealkiri'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='album',
            name='name_sv',
            field=models.CharField(max_length=255, null=True, verbose_name='Pealkiri'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='album',
            name='open',
            field=models.BooleanField(default=False, verbose_name='On avatud (k\xf5ik saavad pilte lisada)'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='albumphoto',
            name='profile',
            field=models.ForeignKey(related_name='album_photo_links', blank=True, to='ajapaik.Profile', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='difficultyfeedback',
            name='user_profile',
            field=models.ForeignKey(related_name='difficulty_feedbacks', to='ajapaik.Profile'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='author',
            field=models.CharField(max_length=255, null=True, verbose_name='Autor', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='description',
            field=models.TextField(null=True, verbose_name='Kirjeldus', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='description_de',
            field=models.TextField(null=True, verbose_name='Kirjeldus', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='description_en',
            field=models.TextField(null=True, verbose_name='Kirjeldus', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='description_et',
            field=models.TextField(null=True, verbose_name='Kirjeldus', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='description_fi',
            field=models.TextField(null=True, verbose_name='Kirjeldus', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='description_nl',
            field=models.TextField(null=True, verbose_name='Kirjeldus', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='description_no',
            field=models.TextField(null=True, verbose_name='Kirjeldus', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='description_ru',
            field=models.TextField(null=True, verbose_name='Kirjeldus', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='description_sv',
            field=models.TextField(null=True, verbose_name='Kirjeldus', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=models.ImageField(height_field=b'height', width_field=b'width', upload_to=b'uploads', max_length=255, blank=True, null=True, verbose_name='Pilt'),
            preserve_default=True,
        ),
    ]
