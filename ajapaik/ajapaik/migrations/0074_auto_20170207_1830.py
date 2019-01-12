# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_comments_xtd', '0002_blacklisteddomain'),
        ('ajapaik', '0073_geotag_photo_flipped'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyXtdComment',
            fields=[
                ('xtdcomment_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='django_comments_xtd.XtdComment')),
            ],
            options={
                'ordering': ('submit_date',),
                'abstract': False,
                'verbose_name': 'comment',
                'verbose_name_plural': 'comments',
                'permissions': [('can_moderate', 'Can moderate comments')],
            },
            bases=('django_comments_xtd.xtdcomment',),
        ),
        migrations.RemoveField(
            model_name='photo',
            name='fb_comments_count',
        ),
        migrations.AddField(
            model_name='photo',
            name='comment_count',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
