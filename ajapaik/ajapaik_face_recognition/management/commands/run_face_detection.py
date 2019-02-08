import datetime
import multiprocessing
from json import dumps

import face_recognition
from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Photo
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle


def analyse_single_photo(photo: Photo) -> None:
    print('Processing photo %s' % photo.pk)
    try:
        image = face_recognition.load_image_file(photo.image)
    except:
        return
    try:
        detected_faces = face_recognition.face_locations(image)
    except:
        return
    for detected_face in detected_faces:
        try:
            new_rectangle = FaceRecognitionRectangle(
                photo=photo,
                coordinates=dumps(detected_face)
            )
            new_rectangle.save()
            photo.face_detection_attempted_at = datetime.datetime.now()
            photo.light_save()
        except:
            continue


class Command(BaseCommand):
    help = 'Will run face detection on all photos in our database that haven\'t had it run yet'

    def handle(self, *args, **options):
        photos = Photo.objects.filter(face_detection_attempted_at__isnull=True).all()
        print('Found %s photos to run on' % photos.count())
        with multiprocessing.Pool() as pool:
            pool.map(analyse_single_photo, photos)
