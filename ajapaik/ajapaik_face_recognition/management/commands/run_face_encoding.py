from json import loads, dumps

import face_recognition
from django.core.management.base import BaseCommand

from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle, FaceRecognitionSubject


class Command(BaseCommand):
    help = 'Will run face encoding on all identified faces'
    args = 'subject_id'

    def handle(self, *args, **options):
        people = FaceRecognitionSubject.objects.all()
        for person in people:
            rectangles_with_this_person = FaceRecognitionRectangle.objects.filter(subject_consensus=person).all()
            for rectangle in rectangles_with_this_person:
                image = face_recognition.load_image_file(rectangle.photo.image)
                encodings = face_recognition.face_encodings(image, known_face_locations=[loads(rectangle.coordinates)])
                if len(encodings) == 1:
                    my_encoding = encodings[0]
                    person.face_encoding = dumps(my_encoding.tolist())
                    person.save()
                else:
                    raise Exception(
                        'Found % face encodings for rectangle %s, should find only 1' % (len(encodings), rectangle.id))
