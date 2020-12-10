from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Album
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle


class Command(BaseCommand):
    help = 'Resets gender of face annotations, that are shown as unsure'

    def handle(self, *args, **options):
        rectangles = FaceRecognitionRectangle.objects.exclude(subject_consensus__isnull=True)
        for rectangle in rectangles:
            album = Album.objects.filter(id=rectangle.subject_consensus.id).first()
            if album.gender:
                rectangle.gender = album.gender
                rectangle.save()
