# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0074_auto_20150526_1554'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhotoComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fb_comment_id', models.CharField(unique=True, max_length=255)),
                ('fb_comment_parent_id', models.CharField(max_length=255, null=True, blank=True)),
                ('fb_user_id', models.CharField(max_length=255)),
                ('text', models.TextField()),
                ('created', models.DateTimeField()),
                ('photo', models.ForeignKey(to='project.Photo')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
