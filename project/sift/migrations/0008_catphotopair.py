# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sift', '0007_remove_catalbum_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatPhotoPair',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('photo1', models.ForeignKey(related_name='pair_first', to='sift.CatPhoto')),
                ('photo2', models.ForeignKey(related_name='pair_second', to='sift.CatPhoto')),
                ('profile', models.ForeignKey(to='sift.CatProfile')),
            ],
            options={
                'db_table': 'project_catphotopair',
            },
            bases=(models.Model,),
        ),
    ]
