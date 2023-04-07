# Generated by Django 3.2.7 on 2023-03-19 20:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0024_auto_20230204_1918'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhotoModelSuggestionConfirmReject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('viewpoint_elevation_to_confirm', models.PositiveSmallIntegerField(blank=True, choices=[(0, 'Ground'), (1, 'Raised'), (2, 'Aerial')], null=True, verbose_name='Viewpoint elevation')),
                ('scene_to_confirm', models.PositiveSmallIntegerField(blank=True, choices=[(0, 'Interior'), (1, 'Exterior')], null=True, verbose_name='Scene')),
                ('viewpoint_elevation_to_reject', models.PositiveSmallIntegerField(blank=True, choices=[(0, 'Ground'), (1, 'Raised'), (2, 'Aerial')], null=True, verbose_name='Viewpoint elevation')),
                ('scene_to_reject', models.PositiveSmallIntegerField(blank=True, choices=[(0, 'Interior'), (1, 'Exterior')], null=True, verbose_name='Scene')),
                ('photo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ajapaik.photo')),
                ('proposer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='photo_scene_suggestions_confirmation', to='ajapaik.profile')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
