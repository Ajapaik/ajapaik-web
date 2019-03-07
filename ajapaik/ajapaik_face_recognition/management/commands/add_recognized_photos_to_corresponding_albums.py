from django.core.management.base import BaseCommand
from django.db.models import Q

from ajapaik.ajapaik.models import AlbumPhoto
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle


class Command(BaseCommand):
    help = 'If we have a rectangle that has a person attached, make sure that photo is in the right album also'

    def handle(self, *args, **options):
        rectangles = FaceRecognitionRectangle.objects.filter(
            Q(subject_consensus__isnull=False) | Q(subject_ai_guess__isnull=False))
        for rectangle in rectangles:
            if rectangle.subject_consensus:
                existing_relation = AlbumPhoto.objects.filter(photo=rectangle.photo, album=rectangle.subject_consensus,
                                                              type=AlbumPhoto.FACE_TAGGED).first()
                if not existing_relation:
                    new_relation = AlbumPhoto(
                        photo=rectangle.photo,
                        album=rectangle.subject_consensus,
                        type=AlbumPhoto.FACE_TAGGED
                    )
                    new_relation.save()
                    print('New relation between %s and %s' % (new_relation.photo.pk, new_relation.album.pk))
            elif rectangle.subject_ai_guess:
                existing_relation = AlbumPhoto.objects.filter(photo=rectangle.photo, album=rectangle.subject_ai_guess,
                                                              type=AlbumPhoto.FACE_TAGGED).first()
                if not existing_relation:
                    new_relation = AlbumPhoto(
                        photo=rectangle.photo,
                        album=rectangle.subject_ai_guess,
                        type=AlbumPhoto.FACE_TAGGED
                    )
                    new_relation.save()
                    print('New relation between %s and %s' % (new_relation.photo.pk, new_relation.album.pk))
