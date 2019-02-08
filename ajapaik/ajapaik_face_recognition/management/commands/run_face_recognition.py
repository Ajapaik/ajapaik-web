import multiprocessing
from json import loads

import face_recognition
import numpy as np
from django.core.management.base import BaseCommand
from dlib import face_recognition_model_v1

from ajapaik.ajapaik.models import Album
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle, FaceRecognitionUserGuess

all_the_people_we_have_faces_for = Album.objects.filter(face_encodings__isnull=False).all()
for each in all_the_people_we_have_faces_for:
    each.loaded_faces = np.array(loads(each.face_encodings))


def recognize_single_rectangle(unrecognized_rectangle: FaceRecognitionRectangle) -> None:
    for person in all_the_people_we_have_faces_for:
        assert isinstance(person, Album)
        comparison_results = face_recognition.compare_faces(person.loaded_faces, np.array(loads(unrecognized_rectangle.face_encoding)))
        if comparison_results[0]:
            unrecognized_rectangle.subject_ai_guess = person
            unrecognized_rectangle.save()

class Command(BaseCommand):
    help = 'Will run face recognition on all rectangles in our database'

    def handle(self, *args, **options):
        # TODO: What if people guess wrong and the computer knows better?
        rectangles_without_known_subjects = FaceRecognitionRectangle.objects.filter(deleted__isnull=True,
                                                                                    subject_consensus__isnull=True,
                                                                                    subject_ai_guess__isnull=True)
        # TODO: This double loop is going to mean a world of pain
        for rectangle in rectangles_without_known_subjects:
            recognize_single_rectangle(rectangle)
        # with multiprocessing.Pool() as pool:
        #     pool.map(recognize_single_rectangle, rectangles_without_known_subjects)

        # for rectangle in rectangles_without_known_subjects:
        #     for person in people:
        #         # TODO: Same code already exists in encoding command, DRY it up
        #         image = face_recognition.load_image_file(rectangle.photo.image)
        #         encodings = face_recognition.face_encodings(image, known_face_locations=[loads(rectangle.coordinates)])
        #         if len(encodings) == 1:
        #             my_encoding = encodings[0]
        #             # FIXME: We can give an array to compare to, this should be orders of magnitude faster
        #             comparison_results = face_recognition.compare_faces([np.array(loads(person.face_encoding))],
        #                                                                 my_encoding)
        #             if comparison_results[0]:
        #                 # Found our person
        #                 FaceRecognitionUserGuess(
        #                     rectangle=rectangle,
        #                     subject=person
        #                 ).save()
        #                 rectangle.subject_ai_guess = person
        #                 rectangle.save()
        #                 rectangle.photo.people.add(person)
        #                 break
        #         else:
        #             raise Exception(
        #                 'Found % face encodings for rectangle %s, should find only 1' % (len(encodings), rectangle.id))
