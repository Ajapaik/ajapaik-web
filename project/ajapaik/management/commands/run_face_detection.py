from json import dumps

import face_recognition
from django.core.management.base import BaseCommand

from project.ajapaik.models import Photo, Album


class Command(BaseCommand):
    help = 'Will run face detection on all photos in our database, specify and album ID if you don\'t want to run on 100k images'
    args = 'album_id'

    def handle(self, *args, **options):
        album_id = args[0]
        if album_id is not None:
            album = Album.objects.filter(pk=album_id).first()
            photos = album.photos.all()
        else:
            photos = Photo.objects.all()
        for photo in photos:
            if not photo.detected_faces:
                image = face_recognition.load_image_file(photo.image)
                photo.detected_faces = dumps(face_recognition.face_locations(image))
                photo.light_save()
