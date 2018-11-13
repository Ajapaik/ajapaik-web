from json import dumps

import face_recognition
from django.core.management.base import BaseCommand

from project.ajapaik.models import Photo, Album, FaceRecognitionRectangle


class Command(BaseCommand):
    help = 'Will run face detection on all photos in our database, specify an album ID if you don\'t want to run on ~100k images'
    args = 'album_id'

    def handle(self, *args, **options):
        album_id = None
        if len(args) > 0:
            album_id = args[0]
        if album_id is not None:
            album = Album.objects.filter(pk=album_id).first()
            # Means computer-detected rectangles are already present, no need to run again
            photos = album.photos.filter(face_recognition_rectangles__user__isnull=True).all()
        else:
            photos = Photo.objects.filter(face_recognition_rectangles__user__isnull=True).all()
        for photo in photos:
            image = face_recognition.load_image_file(photo.image)
            detected_faces = face_recognition.face_locations(image)
            for detected_face in detected_faces:
                new_rectangle = FaceRecognitionRectangle(
                    photo=photo,
                    coordinates=dumps(detected_face)
                )
                new_rectangle.save()
