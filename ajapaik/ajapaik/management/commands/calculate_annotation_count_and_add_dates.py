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
                faceRecognitionRectangles = FaceRecognitionRectangle.objects.all().filter(photo__id=photo.id)
                objectAnnotations = ObjectDetectionAnnotation.objects.all().filter(photo__id=photo.id)
                first = None
                latest = None
                if faceRecognitionRectangles.count() > 0:
                    first = faceRecognitionRectangles.order_by('created').first().created
                    latest = faceRecognitionRectangles.order_by('-modified').first().modified
                if objectAnnotations.count() > 0:
                    if first is None or objectAnnotations.order_by('created_on').first().created_on < first:
                        first = objectAnnotations.order_by('created_on').first().created_on
                    if latest is None or objectAnnotations.order_by('-modified_on').first().modified_on > latest:
                        latest = objectAnnotations.order_by('-modified_on').first().modified_on
                if first:
                    photo.first_annotation = first
                if latest:
                    photo.latest_annotation = latest
                photo.annotation_count = faceRecognitionRectangles.count() + objectAnnotations.count()
                photo.light_save()
            except Exception:
                continue
