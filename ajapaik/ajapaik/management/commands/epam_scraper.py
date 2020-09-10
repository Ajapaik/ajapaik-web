# coding=utf-8
import csv
import io
import json
import os
import requests
import shutil
from django.core.management.base import BaseCommand

# This script was made for a single use, review before running
from ajapaik.ajapaik.models import Source, Album, Photo, Licence, AlbumPhoto
from django.conf import settings


class Command(BaseCommand):
    help = 'Scrape schools from Estonian Pedagogical Archives-Museum'

    def handle(self, *args, **options):
        source = Source.objects.filter(id=219).first()
        album = Album.objects.filter(id=29432).first()
        licence = Licence.objects.filter(id=15).first()
        objects_dict = {}
        files_dict = {}
        selection = os.listdir('/home/ajapaik/ajapaik-web/ajapaik/ajapaik/management/commands/epam_selection')
        with io.open(os.path.dirname(os.path.abspath(__file__)) + '/epam_objects.csv', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row['type'] == 'photo':
                    if 'koolimajad' in row['keywords']:
                        objects_dict[row['id']] = row
        with io.open(os.path.dirname(os.path.abspath(__file__)) + '/epam_files.csv', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row['type'] == 'photo' and 'smallf' not in row['fpath'] and row['object_id'] in objects_dict:
                    files_dict[row['id']] = row['object_id']
        for photo in selection[:100]:
            file_name_parts = photo.split('.')
            object_data = objects_dict[files_dict[file_name_parts[0]]]
            # print(f'Photo {photo}, object data {object_data}')
            source_path = f'/home/ajapaik/ajapaik-web/ajapaik/ajapaik/management/commands/epam_selection/{photo}'
            destination_path = f'/home/ajapaik/ajapaik-web/media/uploads/epam_{photo}'
            shutil.move(source_path, destination_path)
            new_photo = Photo(
                image=f'uploads/epam_{photo}',
                date_text=object_data['date_of_publication'],
                source_key=object_data['archive_id'],
                source_url=f'http://arhmus.tlu.ee/cgi-bin/epam?oid={files_dict[file_name_parts[0]]}',
                source=source,
                description_et=object_data['title_analytic'],
                author=object_data['author_analytic'],
                external_id=file_name_parts[0],
                keywords=object_data['keywords'],
                licence=licence
            )
            new_photo.save()
            if object_data['title_analytic']:
                google_geocode_url = f'https://maps.googleapis.com/maps/api/geocode/json?' \
                                     f'address={object_data["title_analytic"]}&language=en&region=EE&components=country:EE' \
                                     f'&key={settings.GOOGLE_MAPS_API_KEY}'
                google_response_json = requests.get(google_geocode_url).text
                google_response_parsed = json.loads(google_response_json)
                # print(google_response_parsed)
                status = google_response_parsed.get('status', None)
                if status == 'OK':
                    # Google was able to answer some geolocation for this description
                    address = google_response_parsed.get('results')[0].get('formatted_address')
                    lat_lng = google_response_parsed.get('results')[0].get('geometry').get('location')
                    new_photo.lat = lat_lng['lat']
                    new_photo.lon = lat_lng['lng']
                    new_photo.address = address
                    new_photo.save()
            album_photo_relation = AlbumPhoto(
                photo=new_photo,
                album=album,
                type=AlbumPhoto.COLLECTION
            )
            album_photo_relation.save()
            # print(new_photo.__dict__)

        # Code used to retrieve initial photos selection was made of
        # with io.open(os.path.dirname(os.path.abspath(__file__)) + '/epam_objects.csv', encoding='utf-8') as csv_file:
        #     csv_reader = csv.DictReader(csv_file)
        #     line_count = 0
        #     for row in csv_reader:
        #         if line_count == 0:
        #             print(f"Column names are {', '.join(row)}")
        #         else:
        #             if row['type'] == 'photo':
        #                 if 'koolimajad' in row['keywords']:
        #                     schoolhouses_dict[row['id']] = row
        #         line_count += 1
        #
        #     print(f'Processed {line_count} lines.')
        # with io.open(os.path.dirname(os.path.abspath(__file__)) + '/epam_files.csv', encoding='utf-8') as csv_file:
        #     csv_reader = csv.DictReader(csv_file)
        #     line_count = 0
        #     for row in csv_reader:
        #         if line_count == 0:
        #             print(f"Column names are {', '.join(row)}")
        #         else:
        #             if row['type'] == 'photo' and 'smallf' not in row['fpath'] and row['object_id'] in schoolhouses_dict:
        #                 url = f'https://arhmus.tlu.ee/tlibrary/f/{row["fpath"]}'
        #                 response = requests.get(url, stream=True)
        #                 with open(f'{os.path.dirname(os.path.abspath(__file__))}/epam_photos/{row["id"]}.png', 'wb') as out_file:
        #                     shutil.copyfileobj(response.raw, out_file)
        #                 del response
        #         line_count += 1
        #
        #     print(f'Processed {line_count} lines.')
