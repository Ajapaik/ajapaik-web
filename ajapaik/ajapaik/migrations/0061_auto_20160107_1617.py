# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0060_photo_is_then_and_now_rephoto'),
    ]

    operations = [
        migrations.CreateModel(
            name='TourUniqueView',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('profile', models.ForeignKey(related_name='tour_views', to='ajapaik.Profile', on_delete=models.deletion.CASCADE)),
                ('tour', models.ForeignKey(related_name='tour_views', to='ajapaik.Tour', on_delete=models.deletion.CASCADE)),
            ],
            options={
                'db_table': 'thenandnow_touruniqueview',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='touruniqueview',
            unique_together=set([('tour', 'profile')]),
        ),
        migrations.AlterField(
            model_name='tour',
            name='photo_set_type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Valitud fotode tuur'), (1, 'Avatud pildivalik')]),
            preserve_default=True,
        ),
    ]
