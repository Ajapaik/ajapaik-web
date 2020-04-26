# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0016_auto_20151105_1131'),
    ]

    operations = [
        migrations.AddField(
            model_name='dating',
            name='end_accuracy',
            field=models.PositiveSmallIntegerField(default=1, choices=[(0, 'Day'), (1, 'Month'), (2, 'Year')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dating',
            name='start_accuracy',
            field=models.PositiveSmallIntegerField(default=1, choices=[(0, 'Day'), (1, 'Month'), (2, 'Year')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='points',
            name='dating',
            field=models.ForeignKey(blank=True, to='ajapaik.Dating', null=True, on_delete=models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='points',
            name='action',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Geotag'), (1, '\xdclepildistus'), (2, 'Photo upload'), (3, 'Photo curation'), (4, 'Photo re-curation'), (5, 'Dating')]),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='points',
            unique_together=set([('user', 'geotag'), ('user', 'dating')]),
        ),
    ]
