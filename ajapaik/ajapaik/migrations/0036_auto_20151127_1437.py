# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0035_auto_20151125_1557'),
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to=b'videos')),
            ],
            options={
                'db_table': 'project_video',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='album',
            name='videos',
            field=models.ManyToManyField(related_name='albums', to='ajapaik.Video'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='photo',
            name='video',
            field=models.ForeignKey(related_name='stills', blank=True, to='ajapaik.Video', null=True, on_delete=models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='photo',
            name='video_timestamp',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
