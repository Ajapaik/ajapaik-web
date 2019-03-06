# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0089_album_wikidata_qid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='name',
            field=models.CharField(verbose_name='Pealkiri', max_length=255, db_index=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_de',
            field=models.CharField(verbose_name='Pealkiri', max_length=255, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_en',
            field=models.CharField(verbose_name='Pealkiri', max_length=255, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_et',
            field=models.CharField(verbose_name='Pealkiri', max_length=255, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_fi',
            field=models.CharField(verbose_name='Pealkiri', max_length=255, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_nl',
            field=models.CharField(verbose_name='Pealkiri', max_length=255, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_no',
            field=models.CharField(verbose_name='Pealkiri', max_length=255, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_ru',
            field=models.CharField(verbose_name='Pealkiri', max_length=255, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='name_sv',
            field=models.CharField(verbose_name='Pealkiri', max_length=255, null=True, db_index=True),
        ),
    ]
