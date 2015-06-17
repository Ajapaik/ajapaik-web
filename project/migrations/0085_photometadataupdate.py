# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0084_album_ordered'),
    ]

    operations = [
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
                ('photo', models.ForeignKey(related_name='metadata_updates', to='project.Photo')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
