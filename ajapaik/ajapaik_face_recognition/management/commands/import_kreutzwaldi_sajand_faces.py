import csv
import datetime
import io
import json
import os

import face_recognition
from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Album, Photo
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle, FaceRecognitionUserGuess


def intersects(self, other):
    # [top, right, bottom, left]
    return not (self[1] < other[3] or self[3] > other[1] or self[0] > other[2] or self[2] < other[0])


class Command(BaseCommand):
    help = 'Will import new people from kreutzwaldi_sajand_people.csv'

    def handle(self, *args, **options):
        with io.open(os.path.dirname(os.path.abspath(__file__)) + '/kreutzwaldi_sajand_faces.csv',
                     encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    name = row[1].strip()
                    # Top left
                    face_start_x = int(row[4])
                    face_start_y = int(row[5])
                    face_width = int(row[6])
                    face_height = int(row[7])
                    # Bottom right
                    face_end_x = face_start_x + face_width
                    face_end_y = face_start_y + face_height
                    existing_albums = Album.objects.filter(name=name)
                    if existing_albums.count() > 1:
                        print('Found multiple albums matching %s' % name)
                        print(','.join([x.pk for x in existing_albums]))
                        continue
                    elif existing_albums.count() == 0:
                        print('No such person album exists, skipping %s' % name)
                        continue
                    photo = Photo.objects.filter(image__startswith='uploads/%s' % row[0]).first()
                    if not photo:
                        print('Missing matching Photo for %s' % row[0])
                        continue
                    imported_rectangle = FaceRecognitionRectangle(
                        photo=photo,
                        # [top, right, bottom, left]
                        coordinates=json.dumps([face_start_y, face_end_x, face_end_y, face_start_x]),
                        subject_consensus=existing_albums.first(),
                        # Vahur
                        user_id=38,
                        origin=FaceRecognitionRectangle.PICASA
                    )
                    imported_rectangle.save()
                    imported_guess = FaceRecognitionUserGuess(
                        subject_album=existing_albums.first(),
                        rectangle=imported_rectangle,
                        user_id=38,
                        origin=FaceRecognitionUserGuess.PICASA
                    )
                    imported_guess.save()
                    image = face_recognition.load_image_file(photo.image)
                    detected_faces = None
                    try:
                        detected_faces = face_recognition.face_locations(image)
                    except:
                        pass
                    if detected_faces:
                        for detected_face in detected_faces:
                            new_rectangle = FaceRecognitionRectangle(
                                photo=photo,
                                coordinates=json.dumps(detected_face)
                            )
                            if intersects(json.loads(new_rectangle.coordinates),
                                          json.loads(imported_rectangle.coordinates)):
                                # Don't save detected rectangles that intersect with Vahur's
                                print('Intersected!')
                                continue
                            new_rectangle.save()
                    photo.face_detection_attempted_at = datetime.datetime.now()
                    photo.light_save()
                    line_count += 1
            print(f'Processed {line_count} lines.')
