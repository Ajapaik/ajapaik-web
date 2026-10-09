import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ajapaik", "0001_initial"),
        ("ajapaik_face_recognition", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="facerecognitionrectangle",
            name="subject_source_suggestion",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="face_recognition_source_suggested_rectangles",
                to="ajapaik.album",
            ),
        ),
        migrations.AlterField(
            model_name="facerecognitionrectangle",
            name="origin",
            field=models.PositiveSmallIntegerField(
                choices=[(0, "User"), (1, "Algorithm"), (2, "Picasa"), (3, "Fotis")],
                default=1,
            ),
        ),
    ]
