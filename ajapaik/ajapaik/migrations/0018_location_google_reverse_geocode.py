# Generated by Django 3.2.6 on 2021-08-27 23:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0017_auto_20210720_0330'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='google_reverse_geocode',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='google_reverse_geocode',
                to='ajapaik.googlemapsreversegeocode'
                ),
        ),
    ]
