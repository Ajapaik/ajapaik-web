# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0032_dating_confirmation_of'),
    ]

    operations = [
        migrations.CreateModel(
            name='DatingConfirmation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('confirmation_of', models.ForeignKey(related_name='confirmations', to='ajapaik.Dating', on_delete=models.deletion.CASCADE)),
                ('profile', models.ForeignKey(related_name='dating_confirmations', to='ajapaik.Profile', on_delete=models.deletion.CASCADE)),
            ],
            options={
                'db_table': 'project_datingconfirmation',
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='dating',
            name='confirmation_of',
        ),
        migrations.RemoveField(
            model_name='dating',
            name='type',
        ),
        migrations.AddField(
            model_name='points',
            name='dating_confirmation',
            field=models.ForeignKey(blank=True, to='ajapaik.DatingConfirmation', null=True, on_delete=models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dating',
            name='end_accuracy',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(0, 'P\xe4ev'), (1, 'Kuu'), (2, 'Aasta')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dating',
            name='start_accuracy',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(0, 'P\xe4ev'), (1, 'Kuu'), (2, 'Aasta')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='points',
            name='action',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Geot\xe4\xe4g'), (1, '\xdclepildistus'), (2, 'Foto \xfcleslaadimine'), (3, 'Foto kureerimine'), (4, 'Foto rekureerimine'), (5, 'Dateering'), (6, 'Dating confirmation')]),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='points',
            unique_together=set([('user', 'dating_confirmation'), ('user', 'geotag'), ('user', 'dating')]),
        ),
    ]
