import csv
import io
import os
import tempfile

import requests
from django.core import files
from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Album, Photo, AlbumPhoto


# TODO: Remove once we're 100% okay with the album
class Command(BaseCommand):
    help = 'Will import all photos from kreutzwaldi_sajand.csv into album 22614'

    def handle(self, *args, **options):
        album = Album.objects.filter(pk=22614).get()
        with io.open(os.path.dirname(os.path.abspath(__file__)) + '/kreutzwaldi_sajand.csv',
                     encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    response = requests.get(row[4], stream=True)
                    lf = tempfile.NamedTemporaryFile()
                    for block in response.iter_content(1024 * 8):
                        if not block:
                            break
                        lf.write(block)
                    new_picture = Photo(
                        external_id=row[0],
                        source_id=152,
                        source_url=row[1],
                        source_key=row[3],
                        description=row[2]
                    )
                    new_picture.image.save(row[5], files.File(lf))
                    new_picture.save()
                    AlbumPhoto(photo=new_picture, album=album).save()
                    line_count += 1
            print(f'Processed {line_count} lines.')
