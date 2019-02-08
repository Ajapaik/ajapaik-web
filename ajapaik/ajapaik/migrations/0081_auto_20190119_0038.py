# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0080_auto_20181107_2124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='atype',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Curated'), (1, 'Favorites'), (2, 'Auto'), (3, 'Person')]),
        ),
        migrations.AlterField(
            model_name='albumphoto',
            name='type',
            field=models.PositiveSmallIntegerField(db_index=True, default=2, choices=[(0, 'Curated'), (1, 'Re-curated'), (2, 'Manual'), (3, 'Still'), (4, 'Uploaded')]),
        ),
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=models.ImageField(verbose_name='Pilt', max_length=255, blank=True, null=True, upload_to='uploads', width_field='width', height_field='height'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='image_no_watermark',
            field=models.ImageField(max_length=255, blank=True, null=True, upload_to='uploads'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='image_unscaled',
            field=models.ImageField(max_length=255, blank=True, null=True, upload_to='uploads'),
        ),
        migrations.AlterField(
            model_name='tourgroup',
            name='name',
            field=models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F', 'F'), ('G', 'G'), ('H', 'H'), ('I', 'I'), ('J', 'J'), ('K', 'K'), ('L', 'L'), ('M', 'M'), ('N', 'N'), ('O', 'O'), ('P', 'P'), ('Q', 'Q'), ('R', 'R'), ('S', 'S'), ('T', 'T'), ('U', 'U'), ('V', 'V'), ('W', 'W'), ('X', 'X'), ('Y', 'Y'), ('Z', 'Z')]),
        ),
        migrations.AlterField(
            model_name='tourrephoto',
            name='image',
            field=models.ImageField(upload_to='then-and-now', width_field='width', height_field='height'),
        ),
        migrations.AlterField(
            model_name='video',
            name='cover_image',
            field=models.ImageField(blank=True, null=True, upload_to='videos/covers', width_field='cover_image_width', height_field='cover_image_height'),
        ),
        migrations.AlterField(
            model_name='video',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='videos'),
        ),
    ]
