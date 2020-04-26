# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0055_auto_20151218_1135'),
    ]

    operations = [
        migrations.CreateModel(
            name='TourPhotoOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(default=0)),
                ('photo', models.ForeignKey(to='ajapaik.Photo', on_delete=models.deletion.CASCADE)),
                ('tour', models.ForeignKey(to='ajapaik.Tour', on_delete=models.deletion.CASCADE)),
            ],
            options={
                'db_table': 'thenandnow_tourphotoorder',
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='tourphoto',
            name='created',
        ),
        migrations.RemoveField(
            model_name='tourphoto',
            name='modified',
        ),
        migrations.AddField(
            model_name='tour',
            name='photos1',
            field=models.ManyToManyField(to='ajapaik.Photo', null=True, blank=True),
            preserve_default=True,
        ),
    ]
