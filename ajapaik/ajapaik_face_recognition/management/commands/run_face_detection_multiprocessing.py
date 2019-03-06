import json
import multiprocessing
import os

import face_recognition
from django.core.management import BaseCommand


# TODO: Can remove
def analyse_single_photo(photo: dict) -> None:
    print('Processing photo %s' % photo['pk'])
    image = face_recognition.load_image_file(
        'C:/Users/lauri/PycharmProjects/Ajapaik/ajapaik-web/media/' + photo['fields']['image'])
    detected_faces = face_recognition.face_locations(image)
    if detected_faces:
        with open(os.path.dirname(os.path.realpath(__file__)) + '/face_' + str(photo['pk']) + '.json', 'w') as f:
            f.write(json.dumps(detected_faces))


class Command(BaseCommand):
    help = 'Will run face detection on all photos in our database that haven\'t had it run yet'

    def handle(self, *args, **options):
        with open(os.path.dirname(os.path.realpath(__file__)) + '/photos.json') as f:
            photos = json.loads(f.read())[-100:]
        with multiprocessing.Pool() as pool:
            pool.map(analyse_single_photo, photos)
