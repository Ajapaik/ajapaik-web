# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0002_auto_20161008_2119'),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('name_en', models.CharField(max_length=255, null=True)),
                ('name_no', models.CharField(max_length=255, null=True)),
                ('iso_alpha_2_code', models.CharField(max_length=2)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'project_country',
            },
        ),
        migrations.CreateModel(
            name='County',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('name_en', models.CharField(max_length=255, null=True)),
                ('name_no', models.CharField(max_length=255, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('country', models.ForeignKey(related_name='counties', to='ajapaik.Country')),
            ],
            options={
                'db_table': 'project_county',
            },
        ),
        migrations.CreateModel(
            name='Municipality',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('name_en', models.CharField(max_length=255, null=True)),
                ('name_no', models.CharField(max_length=255, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('county', models.ForeignKey(related_name='municipalities', to='ajapaik.County')),
            ],
            options={
                'db_table': 'project_municipality',
            },
        ),
        migrations.AddField(
            model_name='photo',
            name='country',
            field=models.ForeignKey(related_name='photos', default=1, to='ajapaik.Country'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='photo',
            name='county',
            field=models.ForeignKey(related_name='photos', default=1, to='ajapaik.County'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='photo',
            name='municipality',
            field=models.ForeignKey(related_name='photos', default=1, to='ajapaik.Municipality'),
            preserve_default=False,
        ),
    ]
