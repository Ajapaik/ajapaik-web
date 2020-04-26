# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0051_tour_photo_set_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='TourGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=1, choices=[(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ', b'ABCDEFGHIJKLMNOPQRSTUVWXYZ')])),
                ('max_members', models.IntegerField()),
                ('members', models.ManyToManyField(related_name='tour_groups', to='ajapaik.Profile')),
                ('tour', models.ForeignKey(related_name='tour_groups', to='ajapaik.Tour', on_delete=models.deletion.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='tour',
            name='grouped',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tour',
            name='members',
            field=models.ManyToManyField(related_name='tours', to='ajapaik.Profile'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tour',
            name='user',
            field=models.ForeignKey(related_name='owned_tours', to='ajapaik.Profile', on_delete=models.deletion.CASCADE),
            preserve_default=True,
        ),
    ]
