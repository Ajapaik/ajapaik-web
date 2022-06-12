# Generated by Django 3.2.13 on 2022-06-12 17:58

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0023_alter_album_created'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhotoSearchIndex',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(blank=True, null=True)),
                ('text_et', models.TextField(blank=True, null=True)),
                ('text_lv', models.TextField(blank=True, null=True)),
                ('text_lt', models.TextField(blank=True, null=True)),
                ('text_en', models.TextField(blank=True, null=True)),
                ('text_ru', models.TextField(blank=True, null=True)),
                ('text_fi', models.TextField(blank=True, null=True)),
                ('text_sv', models.TextField(blank=True, null=True)),
                ('text_nl', models.TextField(blank=True, null=True)),
                ('text_de', models.TextField(blank=True, null=True)),
                ('text_no', models.TextField(blank=True, null=True)),
                ('vector', django.contrib.postgres.search.SearchVectorField(blank=True, null=True)),
                ('vector_de', django.contrib.postgres.search.SearchVectorField(blank=True, null=True)),
                ('vector_en', django.contrib.postgres.search.SearchVectorField(blank=True, null=True)),
                ('vector_et', django.contrib.postgres.search.SearchVectorField(blank=True, null=True)),
                ('vector_fi', django.contrib.postgres.search.SearchVectorField(blank=True, null=True)),
                ('vector_ru', django.contrib.postgres.search.SearchVectorField(blank=True, null=True)),
                ('vector_lv', django.contrib.postgres.search.SearchVectorField(blank=True, null=True)),
                ('vector_lt', django.contrib.postgres.search.SearchVectorField(blank=True, null=True)),
                ('vector_nl', django.contrib.postgres.search.SearchVectorField(blank=True, null=True)),
                ('vector_no', django.contrib.postgres.search.SearchVectorField(blank=True, null=True)),
                ('vector_sv', django.contrib.postgres.search.SearchVectorField(blank=True, null=True)),
                ('photo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ajapaik.photo')),
            ],
        ),
        migrations.AddIndex(
            model_name='photosearchindex',
            index=django.contrib.postgres.indexes.GinIndex(fields=['vector'], name='text_search_vector_idx'),
        ),
        migrations.AddIndex(
            model_name='photosearchindex',
            index=django.contrib.postgres.indexes.GinIndex(fields=['vector_de'], name='text_search_vector_de_idx'),
        ),
        migrations.AddIndex(
            model_name='photosearchindex',
            index=django.contrib.postgres.indexes.GinIndex(fields=['vector_en'], name='text_search_vector_en_idx'),
        ),
        migrations.AddIndex(
            model_name='photosearchindex',
            index=django.contrib.postgres.indexes.GinIndex(fields=['vector_et'], name='text_search_vector_et_idx'),
        ),
        migrations.AddIndex(
            model_name='photosearchindex',
            index=django.contrib.postgres.indexes.GinIndex(fields=['vector_fi'], name='text_search_vector_fi_idx'),
        ),
        migrations.AddIndex(
            model_name='photosearchindex',
            index=django.contrib.postgres.indexes.GinIndex(fields=['vector_ru'], name='text_search_vector_ru_idx'),
        ),
        migrations.AddIndex(
            model_name='photosearchindex',
            index=django.contrib.postgres.indexes.GinIndex(fields=['vector_lv'], name='text_search_vector_lv_idx'),
        ),
        migrations.AddIndex(
            model_name='photosearchindex',
            index=django.contrib.postgres.indexes.GinIndex(fields=['vector_lt'], name='text_search_vector_lt_idx'),
        ),
        migrations.AddIndex(
            model_name='photosearchindex',
            index=django.contrib.postgres.indexes.GinIndex(fields=['vector_nl'], name='text_search_vector_nl_idx'),
        ),
        migrations.AddIndex(
            model_name='photosearchindex',
            index=django.contrib.postgres.indexes.GinIndex(fields=['vector_no'], name='text_search_vector_no_idx'),
        ),
        migrations.AddIndex(
            model_name='photosearchindex',
            index=django.contrib.postgres.indexes.GinIndex(fields=['vector_sv'], name='text_search_vector_sv_idx'),
        ),
    ]
