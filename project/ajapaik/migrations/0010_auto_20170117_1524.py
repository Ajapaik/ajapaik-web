# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0009_auto_20161114_1713'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='is_public',
            field=models.BooleanField(default=True, verbose_name='Er offentlig'),
        ),
        migrations.AlterField(
            model_name='album',
            name='open',
            field=models.BooleanField(default=False, verbose_name='Er \xe5pen'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='author',
            field=models.CharField(max_length=255, null=True, verbose_name='Opphavsperson', blank=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=models.ImageField(height_field=b'height', width_field=b'width', upload_to=b'uploads', max_length=255, blank=True, null=True, verbose_name='Bilde'),
        ),
    ]
