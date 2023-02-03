from django.core.management.base import BaseCommand
from django.db.models import Q

from ajapaik.ajapaik.models import AlbumPhoto
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle


class Command(BaseCommand):
    help = 'If we have a rectangle that has a person attached, make sure that photo is in the right album also'

    def handle(self, *args, **options):
        rectangles = FaceRecognitionRectangle.objects.filter(
            Q(subject_consensus__isnull=False) | Q(subject_ai_suggestion__isnull=False))
        for rectangle in rectangles:
            subject_album = rectangle.subject_consensus or rectangle.subject_ai_suggestion
            if not subject_album:
                continue
            else:
                existing_relation = AlbumPhoto.objects.filter(photo=rectangle.photo, album=subject_album,
                                                              type=AlbumPhoto.FACE_TAGGED).first()
                if not existing_relation:
                    new_relation = AlbumPhoto(
                        photo=rectangle.photo,
                        album=subject_album,
                        type=AlbumPhoto.FACE_TAGGED
                    )
                    new_relation.save()
                    print('New relation between %s and %s' % (new_relation.photo.pk, new_relation.album.pk))
