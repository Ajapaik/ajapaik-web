import datetime
from json import dumps

import face_recognition
from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Photo
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle


def analyse_single_photo(photo: Photo) -> None:
    if photo.width > 5000 or photo.height > 5000:
        print('Skipping too big photo %s' % photo.pk)
        return
    try:
        image = face_recognition.load_image_file(photo.image)
    except:
        return
    try:
        detected_faces = face_recognition.face_locations(image)
    except:
        return
    for detected_face in detected_faces:
        new_rectangle = FaceRecognitionRectangle(
            photo=photo,
            coordinates=dumps(detected_face)
        )
        new_rectangle.save()
    photo.face_detection_attempted_at = datetime.datetime.now()
    photo.light_save()


class Command(BaseCommand):
    help = 'Will run face detection on all photos in our database that haven\'t had it run yet'

    def handle(self, *args, **options):
        photos = Photo.objects.filter(face_detection_attempted_at__isnull=True).all()
        print('Found %s photos to run on' % photos.count())
        for photo in photos:
            analyse_single_photo(photo)
