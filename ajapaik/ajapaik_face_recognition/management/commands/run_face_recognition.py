from json import loads

import face_recognition
import numpy as np
from django.core.management.base import BaseCommand

from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle, FaceRecognitionSubject, \
    FaceRecognitionUserGuess


class Command(BaseCommand):
    help = 'Will run face recognition on all rectangles in our database'

    def handle(self, *args, **options):
        # TODO: This kind of things need to be run in multiple threads to have any luck succeeding
        # TODO: What if people guess wrong and the computer knows better?
        rectangles_without_known_subjects = FaceRecognitionRectangle.objects.filter(deleted__isnull=True,
                                                                                    subject_consensus__isnull=True,
                                                                                    subject_ai_guess__isnull=True)
        people = FaceRecognitionSubject.objects.filter(face_encoding__isnull=False).all()
        for rectangle in rectangles_without_known_subjects:
            for person in people:
                # TODO: Same code already exists in encoding command, DRY it up
                image = face_recognition.load_image_file(rectangle.photo.image)
                encodings = face_recognition.face_encodings(image, known_face_locations=[loads(rectangle.coordinates)])
                if len(encodings) == 1:
                    my_encoding = encodings[0]
                    # FIXME: We can give an array to compare to, this should be orders of magnitude faster
                    comparison_results = face_recognition.compare_faces([np.array(loads(person.face_encoding))],
                                                                        my_encoding)
                    if comparison_results[0]:
                        # Found our person
                        FaceRecognitionUserGuess(
                            rectangle=rectangle,
                            subject=person
                        ).save()
                        rectangle.subject_ai_guess = person
                        rectangle.save()
                        rectangle.photo.people.add(person)
                        break
                else:
                    raise Exception(
                        'Found % face encodings for rectangle %s, should find only 1' % (len(encodings), rectangle.id))
