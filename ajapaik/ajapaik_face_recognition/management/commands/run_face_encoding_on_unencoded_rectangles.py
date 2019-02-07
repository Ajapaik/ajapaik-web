import multiprocessing
from copyreg import pickle
from json import loads, dumps
import pickle
import face_recognition
from django.core.management.base import BaseCommand

from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle


def encode_single_rectangle(rectangle: FaceRecognitionRectangle) -> None:
    print('Processing rectangle %s' % rectangle.pk)
    try:
        image = face_recognition.load_image_file(rectangle.photo.image)
    except:
        return
    try:
        encodings = face_recognition.face_encodings(image, known_face_locations=[loads(rectangle.coordinates)])
    except:
        return
    if len(encodings) == 1:
        my_encoding = encodings[0]
        try:
            rectangle.face_encoding = dumps(my_encoding.tolist())
            rectangle.save()
        except:
            return
    else:
        print('Found % face encodings for rectangle %s, should find only 1' % (len(encodings), rectangle.id))


class Command(BaseCommand):
    help = 'Will run face encoding on all identified faces'
    args = 'subject_id'

    def handle(self, *args, **options):
        unknown_rectangles = FaceRecognitionRectangle.objects.filter(face_encoding__isnull=True).all()
        print('Found %s rectangles to run on' % unknown_rectangles.count())
        with multiprocessing.Pool() as pool:
            pool.map(encode_single_rectangle, unknown_rectangles)
