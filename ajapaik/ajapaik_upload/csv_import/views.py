import csv
import os
import shutil
import stat
from uuid import uuid4
from zipfile import ZipFile

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib.gis.geos import Point
from django.core.files.storage import default_storage
from django.shortcuts import render

from ajapaik.ajapaik.forms import CsvImportForm
from ajapaik.ajapaik.models import Photo, Licence, Source, GeoTag, Album, AlbumPhoto, Points
from ajapaik.ajapaik.utils import ImportBlacklistService


@user_passes_test(lambda u: u.groups.filter(name='csv_uploaders').exists(), login_url='/admin/')
def csv_import(request):
    if request.method == 'GET':
        form = CsvImportForm
        return render(request, 'csv/csv-import.html', {'form': form})

    if request.method == 'POST':
        csv_file = request.FILES['csv_file']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        existing_file_list = []
        errors = []
        file_list = []
        missing_album_list = []
        missing_licence_list = []
        not_found_list = []
        profile = request.get_user().profile
        skipped_list = []
        blacklisted_list = []
        success = None
        unique_album_list = []
        upload_folder = f'{settings.MEDIA_ROOT}/uploads/'
        final_image_folder = 'uploads/'

        if 'zip_file' in request.FILES:
            file_obj = request.FILES['zip_file']
            import_folder = f'{settings.MEDIA_ROOT}/import'
            zip_filename = f'{settings.MEDIA_ROOT}/import{str(uuid4())}.zip'

            with default_storage.open(zip_filename, 'wb+') as destination:
                for chunk in file_obj.chunks():
                    destination.write(chunk)

            with ZipFile(zip_filename, 'r') as zip_ref:
                zip_ref.extractall(import_folder)

            file_names = os.listdir(import_folder)
            for name in file_names:
                if '.' in name:
                    os.chmod(f'{import_folder}/{name}', 0o0664)
                    if not os.path.exists(f'{upload_folder}/{name}'):
                        shutil.move(os.path.join(import_folder, name), upload_folder)
                    else:
                        existing_file_list.append(upload_folder + name)
                        os.remove(f'{import_folder}/{name}')
                else:
                    def del_evenReadonly(action, name, exc):
                        os.chmod(name, stat.S_IWRITE)
                        os.remove(name)

                    shutil.rmtree(f'{import_folder}/{name}', onerror=del_evenReadonly)
            os.remove(zip_filename)
            os.rmdir(import_folder)

        for row in csv.DictReader(decoded_file, delimiter=',', quotechar='"'):
            file_list.append(final_image_folder + row['file'])

        existing_photos = Photo.objects.filter(image__in=file_list).values_list('image', flat=True)

        import_blacklist_service = ImportBlacklistService()

        # TODO: map over row fields instead to directly set attributes of photo with setattr
        # before doing so remove any exceptions like album, source, licence or start using only ids
        for row in csv.DictReader(decoded_file, delimiter=',', quotechar='"'):
            if existing_photos.exists() and f"{upload_folder}{row['file']}" in list(existing_photos):
                skipped_list.append(row['file'])
                continue
            album_ids = row['album'].replace(' ', '').split(',')
            person_album_ids = row['person_album'].replace(' ', '').split(',')
            author = None
            keywords = None
            geography = None
            lat = None
            lon = None
            licence = None
            source = None
            source_url = None
            source_key = None
            date_text = None
            description = None
            description_et = None
            description_en = None
            description_fi = None
            description_ru = None
            title = None
            title_et = None
            title_en = None
            title_fi = None
            title_ru = None
            types = None
            if 'author' in row.keys():
                author = row['author']
            if 'keywords' in row.keys():
                keywords = row['keywords']
            if 'lat' in row.keys() and row['lat'] != '':
                lat = row['lat']
            if 'lon' in row.keys() and row['lon'] != '':
                lon = row['lon']
            if lat and lon:
                geography = Point(x=float(lon), y=float(lat), srid=4326)
            if 'licence' in row.keys():
                licence = Licence.objects.filter(id=row['licence']).first()
                if licence is None and not row['licence'] in missing_licence_list:
                    missing_licence_list.append(row['licence'])
            if 'source' in row.keys():
                source = Source.objects.filter(id=row['source']).first()
            if 'source_key' in row.keys():
                source_key = row['source_key']

                if source_key and import_blacklist_service.is_blacklisted(source_key):
                    blacklisted_list.append(row['file'])
                    continue

            if 'source_url' in row.keys():
                source_url = row['source_url']
            if 'date_text' in row.keys():
                date_text = row['date_text']
            if 'description' in row.keys():
                description = row['description']
            if 'description_et' in row.keys():
                description_et = row['description_et']
            if 'description_en' in row.keys():
                description_en = row['description_en']
            if 'description_fi' in row.keys():
                description_fi = row['description_fi']
            if 'description_ru' in row.keys():
                description_ru = row['description_ru']
            if 'title' in row.keys():
                title = row['title']
            if 'title_et' in row.keys():
                title_et = row['title_et']
            if 'title_en' in row.keys():
                title_en = row['title_en']
            if 'title_fi' in row.keys():
                title_fi = row['title_fi']
            if 'title_ru' in row.keys():
                title_ru = row['title_ru']
            if 'types' in row.keys():
                types = row['types']

            try:
                photo = Photo(
                    image=upload_folder + row['file'],
                    author=author,
                    keywords=keywords,
                    lat=lat,
                    lon=lon,
                    geography=geography,
                    source=source,
                    source_key=source_key,
                    source_url=source_url,
                    date_text=date_text,
                    licence=licence,
                    user=profile,
                    description=description,
                    title=title,
                    types=types
                )
                photo.save()
                photo = Photo.objects.get(id=photo.id)
                photo.image.name = final_image_folder + row['file']
                if description_et:
                    photo.description_et = description_et
                if description_en:
                    photo.description_en = description_en
                if description_fi:
                    photo.description_fi = description_fi
                if description_ru:
                    photo.description_ru = description_ru
                if title_et:
                    photo.title_et = title_et
                if title_en:
                    photo.title_en = title_en
                if title_fi:
                    photo.title_fi = title_fi
                if title_ru:
                    photo.title_ru = title_ru
                photo.light_save()

                if geography:
                    geotag = GeoTag(
                        lat=lat,
                        lon=lon,
                        origin=GeoTag.SOURCE,
                        type=GeoTag.SOURCE_GEOTAG,
                        map_type=GeoTag.NO_MAP,
                        photo=photo,
                        is_correct=True,
                        trustworthiness=0.07,
                        geography=geography,
                    )
                    geotag.save()
            except FileNotFoundError as not_found:
                not_found_list.append(not_found.filename.replace(upload_folder, ''))
                continue

            for album_id in album_ids:
                try:
                    album_id = int(album_id)
                except Exception as e:
                    print(e)
                    continue
                album = Album.objects.filter(id=album_id).first()
                if album is None:
                    missing_album_list.append(album_id)
                else:
                    if album_id not in unique_album_list:
                        unique_album_list.append(album_id)
                    ap = AlbumPhoto(photo=photo, album=album, type=AlbumPhoto.CURATED)
                    ap.save()

                    action = Points.PHOTO_CURATION
                    points = 50
                    points_for_curating = Points(
                        action=action,
                        photo=photo,
                        points=points,
                        user=profile,
                        created=photo.created,
                        album=album
                    )
                    points_for_curating.save()

                    if not album.cover_photo:
                        album.cover_photo = photo
                        album.light_save()

            for person_album_id in person_album_ids:
                try:
                    person_album_id = int(person_album_id)
                except Exception as e:
                    print(e)
                    continue
                album = Album.objects.filter(id=person_album_id).first()
                if album is None:
                    missing_album_list.append(person_album_id)
                else:
                    if person_album_id not in unique_album_list:
                        unique_album_list.append(person_album_id)
                    ap = AlbumPhoto(photo=photo, album=album, type=AlbumPhoto.FACE_TAGGED)
                    ap.save()

                    if not album.cover_photo:
                        album.cover_photo = photo
                        album.light_save()
        all_albums = Album.objects.filter(id__in=unique_album_list)
        if all_albums.exists():
            for album in all_albums:
                album.set_calculated_fields()
                album.save()
        if len(existing_file_list) > 0:
            existing_file_error = 'The following images already existed on the server, they were not replaced:'
            errors.append({'message': existing_file_error, 'list': list(set(existing_file_list))})
        if len(missing_licence_list) > 0:
            missing_licence_error = 'The following licences do not exist:'
            errors.append({'message': missing_licence_error, 'list': list(set(missing_licence_list))})
        if len(missing_album_list) > 0:
            missing_albums_error = "The albums with following IDs do not exist:"
            errors.append({'message': missing_albums_error, 'list': list(set(missing_album_list))})
        if len(not_found_list) > 0:
            missing_files_error = "Some files are missing from disk, thus they were not added:"
            errors.append({'message': missing_files_error, 'list': list(set(not_found_list))})
        if len(skipped_list) > 0:
            already_exists_error = "Some imports were skipped since they already exist on Ajapaik:"
            errors.append({'message': already_exists_error, 'list': list(set(skipped_list))})
        if len(blacklisted_list) > 0:
            blacklisted_error = "Some images are blacklisted from Ajapaik, they were not added"
            errors.append({'message': blacklisted_error, 'list': list(set(blacklisted_list))})
        if len(errors) < 1:
            success = 'OK'

        form = CsvImportForm
        return render(request, 'csv/csv-import.html', {'form': form, 'errors': errors, 'success': success})
