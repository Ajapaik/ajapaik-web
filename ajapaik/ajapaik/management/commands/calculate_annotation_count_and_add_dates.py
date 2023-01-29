from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Photo
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle
from ajapaik.ajapaik_object_recognition.models import ObjectDetectionAnnotation


class Command(BaseCommand):
    help = 'Count annotations and update photo to reflect the count'

    def handle(self, *args, **options):
        photos = Photo.objects.all()
        for photo in photos:
            try:
                face_recognition_rectangles = FaceRecognitionRectangle.objects.all().filter(photo__id=photo.id)
                object_annotations = ObjectDetectionAnnotation.objects.all().filter(photo__id=photo.id)
                first = None
                latest = None
                if face_recognition_rectangles.exists():
                    first = face_recognition_rectangles.order_by('created').first().created
                    latest = face_recognition_rectangles.order_by('-modified').first().modified
                if object_annotations.exists():
                    if first is None or object_annotations.order_by('created_on').first().created_on < first:
                        first = object_annotations.order_by('created_on').first().created_on
                    if latest is None or object_annotations.order_by('-modified_on').first().modified_on > latest:
                        latest = object_annotations.order_by('-modified_on').first().modified_on
                if first:
                    photo.first_annotation = first
                if latest:
                    photo.latest_annotation = latest
                photo.annotation_count = face_recognition_rectangles.count() + object_annotations.count()
                photo.light_save()
            except Exception:
                continue
