# Generated by Django 3.2.20 on 2024-07-08 19:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('ajapaik', '0025_importblacklist'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='soft_deleted',
            field=models.BooleanField(default=False, help_text='Hide image from being accessed, even in ADMIN!'),
        ),
    ]
