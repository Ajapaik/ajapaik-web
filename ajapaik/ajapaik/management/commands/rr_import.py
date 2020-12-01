# coding=utf-8
import csv
import io
import os
import shutil

from django.core.management.base import BaseCommand

# This script was made for a single use, review before running
from ajapaik.ajapaik.models import Source, Album, Licence, Photo, AlbumPhoto


class Command(BaseCommand):
    help = 'Copy over some pics of Rahvusraamatukogu'

    def handle(self, *args, **options):
        source = Source.objects.filter(id=77).first()
        main_album = Album.objects.filter(id=29495).first()
        interior_album = Album.objects.filter(id=11891).first()
        licence = Licence.objects.filter(id=15).first()
        with io.open(os.path.dirname(os.path.abspath(__file__)) + '/RR pildid Ajapaika.csv',
                     encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                source_path = f'/home/ajapaik/ajapaik-web/ajapaik/ajapaik/management/commands/' \
                              f'ajapaik_RR2/{row["filename"]}'
                destination_path = f'/home/ajapaik/ajapaik-web/media/uploads/rr2_{row["filename"]}'
                shutil.move(source_path, destination_path)
                new_photo = Photo(
                    image=f'uploads/rr2_{row["filename"]}',
                    licence=licence,
                    source=source,
                    date_text=row['date'],
                    description_et=row['title']
                )
                if row['author']:
                    new_photo.author = row['author']
                new_photo.save()
                album_photo_relation = AlbumPhoto(
                    photo=new_photo,
                    album=main_album,
                    type=AlbumPhoto.COLLECTION
                )
                album_photo_relation.save()
                if row['is_interior'] == '1':
                    album_photo_relation = AlbumPhoto(
                        photo=new_photo,
                        album=interior_album,
                        type=AlbumPhoto.COLLECTION
                    )
                    album_photo_relation.save()
