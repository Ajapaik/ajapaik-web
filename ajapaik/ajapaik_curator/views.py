import datetime
import json
import os
import ssl
import traceback
from urllib.request import build_opener

import threading
import time

import requests
from PIL import Image, ImageOps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.db import close_old_connections
from django.db.models import Q, F
from django.db.transaction import atomic
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from rest_framework.renderers import JSONRenderer

from ajapaik.ajapaik.forms import CuratorWholeSetAlbumsSelectionForm, CuratorAlbumEditForm, CuratorPhotoUploadForm
from ajapaik.ajapaik.fotis_utils import parse_fotis_timestamp_data
from ajapaik.ajapaik.models import Album, AlbumPhoto, Photo, Licence, Source, GeoTag, Points, Dating, \
    ApplicationException, CuratorImportItem
from ajapaik.ajapaik.serializers import CuratorAlbumSelectionAlbumSerializer, \
    CuratorAlbumInfoSerializer
from ajapaik.ajapaik.utils import ImportBlacklistService, _join_2_json_objects
from ajapaik.ajapaik_curator.curator_drivers.common import CuratorSearchForm
from ajapaik.ajapaik_curator.curator_drivers.europeana import EuropeanaDriver
from ajapaik.ajapaik_curator.curator_drivers.finna import FinnaDriver
from ajapaik.ajapaik_curator.curator_drivers.flickr_commons import FlickrCommonsDriver
from ajapaik.ajapaik_curator.curator_drivers.fotis import FotisDriver
from ajapaik.ajapaik_curator.curator_drivers.valimimoodul import ValimimoodulDriver
from ajapaik.ajapaik_curator.curator_drivers.wikimediacommons import CommonsDriver
from ajapaik.ajapaik_curator.utils import _get_licence_name_from_url


@ensure_csrf_cookie
def curator(request):
    last_created_album = Album.objects.filter(is_public=True).order_by('-created').first()
    if last_created_album and last_created_album.photo_count_with_subalbums > 5:
        curator_random_image_ids = AlbumPhoto.objects.filter(
            album_id=last_created_album.id).order_by('?').values_list('photo_id', flat=True)
    else:
        curator_random_image_ids = AlbumPhoto.objects.order_by('?').values_list('photo_id', flat=True)

    image_count = min(5, curator_random_image_ids.count())
    curator_random_images = Photo.objects.filter(pk__in=curator_random_image_ids)[:image_count]
    context = {
        'description': _('Search for old photos, add them to Ajapaik, '
                         'determine their locations and share the resulting album!'),
        'curator_random_images': curator_random_images,
        'hostname': f"{request.scheme}://{request.get_host()}",
        'is_curator': True,
        'CURATOR_FLICKR_ENABLED': settings.CURATOR_FLICKR_ENABLED,
        'CURATOR_EUROPEANA_ENABLED': settings.CURATOR_EUROPEANA_ENABLED,
        'ajapaik_facebook_link': settings.AJAPAIK_FACEBOOK_LINK,
        'whole_set_albums_selection_form': CuratorWholeSetAlbumsSelectionForm()
    }

    return render(request, 'curator/curator.html', context)


def curator_search(request):
    form = CuratorSearchForm(request.POST)
    response = json.dumps({})
    if form.is_valid():

        if form.cleaned_data['useMUIS'] or form.cleaned_data['useMKA'] or form.cleaned_data['useDIGAR'] or \
                form.cleaned_data['useETERA'] or form.cleaned_data['useUTLIB']:

            valimimoodul_driver = ValimimoodulDriver()

            if form.cleaned_data['ids']:
                response = valimimoodul_driver.transform_response(
                    valimimoodul_driver.get_by_ids(form.cleaned_data['ids']),
                    form.cleaned_data['filterExisting'])

        else:
            valimimoodul_driver = None

        if form.cleaned_data['fullSearch']:
            if valimimoodul_driver and not form.cleaned_data['ids']:
                response = _join_2_json_objects(response, valimimoodul_driver.transform_response(
                    valimimoodul_driver.search(form.cleaned_data), form.cleaned_data['filterExisting']))

            if form.cleaned_data['useFlickr']:
                flickr_driver = FlickrCommonsDriver()
                response = _join_2_json_objects(response, flickr_driver.transform_response(
                    flickr_driver.search(form.cleaned_data), form.cleaned_data['filterExisting']))

            if form.cleaned_data['useCommons']:
                commons_driver = CommonsDriver()
                response = _join_2_json_objects(response, commons_driver.transform_response(
                    commons_driver.search(form.cleaned_data), form.cleaned_data['filterExisting']))

            if form.cleaned_data['useEuropeana']:
                europeana_driver = EuropeanaDriver()
                response = _join_2_json_objects(response, europeana_driver.transform_response(
                    europeana_driver.search(form.cleaned_data), form.cleaned_data['filterExisting']))

            if form.cleaned_data['useFinna']:
                finna_driver = FinnaDriver()
                response = _join_2_json_objects(response, finna_driver.transform_response(
                    finna_driver.search(form.cleaned_data), form.cleaned_data['filterExisting'],
                    form.cleaned_data['driverPage']))

            if form.cleaned_data['useFotis']:
                fotis_driver = FotisDriver()
                fotis_data = fotis_driver.search(form.cleaned_data)
                response = _join_2_json_objects(response, fotis_driver.transform_response(fotis_data, form.cleaned_data[
                    'filterExisting']))

    return HttpResponse(response, content_type='application/json')


def curator_my_album_list(request):
    user_profile = request.get_user().profile
    albums = Album.objects.filter(Q(profile=user_profile, atype__in=[Album.CURATED, Album.PERSON])).order_by('-created')

    data = []
    for a in albums:
        data.append({
            'id': a.id,
            'name': a.name,
            'photo_count': a.photo_count_with_subalbums,
        })
    return HttpResponse(json.dumps(data), content_type='application/json')


def curator_import_list(request):
    user_profile = request.get_user().profile
    # Filter for AUTO albums created by this user
    albums = Album.objects.filter(profile=user_profile, atype=Album.AUTO).order_by('-created')

    data = []
    for album in albums:
        data.append({
            'id': album.id,
            'name': album.name,
            'created': album.created.isoformat(),
            'photo_count': album.photos.count()
        })

    return JsonResponse(data, safe=False)


def curator_selectable_albums(request):
    user_profile = request.get_user().profile
    serializer = CuratorAlbumSelectionAlbumSerializer(
        Album.objects.filter(((Q(profile=user_profile) | Q(is_public=True)) & ~Q(atype=Album.AUTO)) | (
                Q(open=True) & ~Q(atype=Album.AUTO))).order_by('name').all(), many=True
    )

    return HttpResponse(JSONRenderer().render(serializer.data), content_type='application/json')


def curator_get_album_info(request):
    album_id = request.POST.get('albumId') or None
    if album_id is not None:
        try:
            album = Album.objects.get(pk=album_id)
            serializer = CuratorAlbumInfoSerializer(album)
        except ObjectDoesNotExist:
            return HttpResponse('Album does not exist', status=404)
        return HttpResponse(JSONRenderer().render(serializer.data), content_type='application/json')
    return HttpResponse('No album ID', status=500)


def curator_update_my_album(request):
    album_edit_form = CuratorAlbumEditForm(request.POST)
    is_valid = album_edit_form.is_valid()
    album_id = album_edit_form.cleaned_data['album_id']
    user_profile = request.get_user().profile
    if is_valid and album_id and user_profile:
        try:
            album = Album.objects.get(pk=album_id, profile=user_profile)
        except ObjectDoesNotExist:
            return HttpResponse('Album does not exist', status=404)

        album.name = album_edit_form.cleaned_data['name']
        album.description = album_edit_form.cleaned_data['description']
        album.open = album_edit_form.cleaned_data['open']
        album.is_public = album_edit_form.cleaned_data['is_public']

        if album_edit_form.cleaned_data['areaLat'] and album_edit_form.cleaned_data['areaLng']:
            album.lat = album_edit_form.cleaned_data['areaLat']
            album.lon = album_edit_form.cleaned_data['areaLng']

        parent_album_id = album_edit_form.cleaned_data['parent_album_id']
        if parent_album_id:
            try:
                parent_album = Album.objects.exclude(id=album.id).get(
                    Q(profile=user_profile, is_public=True, pk=parent_album_id) | Q(open=True, pk=parent_album_id))
                album.subalbum_of = parent_album
            except ObjectDoesNotExist:
                return HttpResponse("Invalid parent album", status=500)
        else:
            album.subalbum_of = None

        album.save()

        return HttpResponse('OK', status=200)

    return HttpResponse('Faulty data', status=500)


_worker_lock = threading.Lock()
_worker_running = False


def _resolve_curator_licence(institution, licence_str, licence_url):
    unknown_licence = Licence.objects.get(pk=15)
    if institution == 'Flickr Commons':
        flickr_licence = Licence.objects.filter(url='https://www.flickr.com/commons/usage/').first()
        return flickr_licence or unknown_licence
    if institution and institution.split(',')[0] == 'ETERA':
        return unknown_licence
    if not institution and licence_str:
        licence_id = dict(Licence.objects.values_list('name', 'id')).get(licence_str) or \
                     dict(Licence.objects.values_list('url', 'id')).get(licence_url)
        if not licence_id:
            licence_name = licence_str if licence_str != licence_url else _get_licence_name_from_url(licence_url)
            return Licence.objects.create(name=licence_name, url=licence_url)
        return Licence.objects.get(pk=licence_id)
    return unknown_licence


def _resolve_curator_source_id(institution):
    if not institution:
        return dict(Source.objects.values_list('name', 'id')).get('AJP')
    source_id = dict(Source.objects.values_list('description', 'id')).get(institution)
    if not source_id:
        source = Source.objects.create(name=institution, description=institution)
        source_id = source.id
    return source_id


def _parse_curator_muis_ids(incoming_id, url_to_record, is_digar):
    if is_digar:
        return incoming_id, 1
    if '_' in incoming_id and 'finna.fi' not in url_to_record and 'europeana.eu' not in url_to_record:
        parts = incoming_id.split('_', 1)
        return parts[0], parts[1]
    return incoming_id, None


def _handle_curator_existing_photo(item, existing_photo, general_albums, default_album, profile):
    for a in general_albums:
        AlbumPhoto.objects.create(photo=existing_photo, album=a, profile=profile,
                                  type=AlbumPhoto.RECURATED)
        Points.objects.create(user=profile, action=Points.PHOTO_RECURATION,
                              photo=existing_photo, points=30, album=a, created=timezone.now())
    if default_album:
        AlbumPhoto.objects.create(photo=existing_photo, album=default_album, profile=profile,
                                  type=AlbumPhoto.RECURATED)
    item.status = CuratorImportItem.SUCCESS
    item.result_photo = existing_photo
    item.save(update_fields=['status', 'result_photo', 'modified'])
    return True


def _fetch_meediateek_image(muis_id):
    meediateek_url = f'https://www.meediateek.ee/photo/full?id={muis_id}'
    meediateek_headers = {
        'User-Agent': settings.UA,
        'Referer': f'https://www.meediateek.ee/photo/view?id={muis_id}'
    }
    for attempt in range(3):
        try:
            res = requests.get(
                meediateek_url,
                headers=meediateek_headers,
                timeout=15,
                allow_redirects=False
            )
            if res.status_code == 200 and 'image' in res.headers.get('Content-Type', ''):
                return res.content
            if res.status_code in (500, 502, 503, 504) and attempt < 2:
                time.sleep(1.5)
            else:
                break
        except (requests.RequestException, ssl.SSLError):
            if attempt < 2:
                time.sleep(1.5)
    return None


def _fetch_fallback_image(image_url, etera_token):
    for attempt in range(3):
        try:
            ssl._create_default_https_context = ssl._create_unverified_context
            opener = build_opener()
            headers = [('User-Agent', settings.UA)]
            if etera_token:
                headers.append(('Authorization', f'Bearer {etera_token}'))
            opener.addheaders = headers
            img_response = opener.open(image_url, timeout=15)
            content = img_response.read()
            if content:
                return content
        except Exception:
            if attempt < 2:
                time.sleep(1.5)
            else:
                raise
    return None


def _save_photo_image(photo, institution, muis_id, image_url, etera_token):
    img_content = None
    if institution == 'Fotis' and muis_id:
        img_content = _fetch_meediateek_image(muis_id)
    if not img_content:
        img_content = _fetch_fallback_image(image_url, etera_token)

    if photo.source and 'ETERA' in photo.source.description:
        photo.image_no_watermark.save('etera.jpg', ContentFile(img_content))
        photo.watermark()
    else:
        photo.image.save('muis.jpg', ContentFile(img_content))


def _apply_photo_transforms(photo):
    if not (photo.invert or photo.rotated or photo.flip):
        return None
    photo_path = f'{settings.MEDIA_ROOT}/{str(photo.image)}'
    img = Image.open(photo_path)
    if photo.invert:
        img = ImageOps.invert(img).convert('L')
        img.save(photo_path)
    if photo.rotated:
        img = img.rotate(photo.rotated, expand=1)
        img.save(photo_path)
        photo.width, photo.height = img.size
    if photo.flip:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        img.save(photo_path)
    return photo_path


def _handle_curator_geotag(photo, lat, lng):
    if not (lat and lng):
        return
    gt_exists = GeoTag.objects.filter(type=GeoTag.SOURCE_GEOTAG, photo__source_key=photo.source_key).exists()
    if not gt_exists:
        source_geotag = GeoTag.objects.create(
            lat=lat,
            lon=lng,
            origin=GeoTag.SOURCE,
            type=GeoTag.SOURCE_GEOTAG,
            map_type=GeoTag.NO_MAP,
            photo=photo,
            is_correct=True,
            trustworthiness=0.07
        )
        photo.latest_geotag = source_geotag.created
        photo.set_calculated_fields()


def _link_curator_albums_and_points(photo, general_albums, default_album, profile):
    first_general_album = general_albums.first()
    Points.objects.create(
        action=Points.PHOTO_CURATION,
        photo=photo,
        points=50,
        user=profile,
        created=photo.created,
        album=first_general_album
    )
    if general_albums.exists():
        for a in general_albums:
            AlbumPhoto.objects.create(photo=photo, album=a, profile=profile, type=AlbumPhoto.CURATED)
            if not a.cover_photo:
                a.cover_photo = photo
                a.light_save()

        for b in general_albums[1:]:
            Points.objects.create(
                action=Points.PHOTO_RECURATION,
                photo=photo,
                points=30,
                user=profile,
                created=photo.created,
                album=b
            )

    if default_album:
        AlbumPhoto.objects.create(photo=photo, album=default_album, profile=profile, type=AlbumPhoto.CURATED)

    if general_albums.exists():
        general_albums.update(photo_count_with_subalbums=F('photo_count_with_subalbums') + 1)
        parent_ids = list(general_albums.filter(subalbum_of__isnull=False).values_list('subalbum_of_id', flat=True))
        if parent_ids:
            Album.objects.filter(id__in=parent_ids).update(
                photo_count_with_subalbums=F('photo_count_with_subalbums') + 1
            )
        general_albums.filter(cover_photo=None).update(cover_photo=photo)


def _link_curator_persons(photo, persons, lat, lng):
    if not persons:
        return
    existing_albums = Album.objects.filter(name__in=persons, atype=Album.PERSON)
    album_ids = list(existing_albums.values_list('id', flat=True))
    for album in existing_albums:
        AlbumPhoto.objects.create(photo=photo, album=album, type=AlbumPhoto.FACE_TAGGED)

    existing_names = set(existing_albums.values_list('name', flat=True))
    new_names = list(set(persons) - existing_names)
    for person_name in new_names:
        album = Album.objects.create(name=person_name, atype=Album.PERSON)
        album_ids.append(album.id)
        AlbumPhoto.objects.create(photo=photo, album=album, type=AlbumPhoto.FACE_TAGGED)

    affected_albums = Album.objects.filter(id__in=album_ids)
    affected_albums.update(photo_count_with_subalbums=F('photo_count_with_subalbums') + 1)
    if lat and lng:
        affected_albums.update(geotagged_photo_count_with_subalbums=F('geotagged_photo_count_with_subalbums') + 1)
    affected_albums.filter(cover_photo=None).update(cover_photo=photo)


def _link_curator_dating(photo, upload_form):
    start_date = upload_form.cleaned_data.get('start_date')
    end_date = upload_form.cleaned_data.get('end_date')
    if not (start_date or end_date):
        return
    date_start_accuracy = upload_form.cleaned_data.get('date_start_accuracy')
    date_end_accuracy = upload_form.cleaned_data.get('date_end_accuracy')
    start_accuracy, raw_start_pattern = parse_fotis_timestamp_data(date_start_accuracy)
    end_accuracy, raw_end_pattern = parse_fotis_timestamp_data(date_end_accuracy)
    raw_start = datetime.datetime.fromisoformat(start_date).strftime(raw_start_pattern) if start_date else None
    raw_end = datetime.datetime.fromisoformat(end_date).strftime(raw_end_pattern) if end_date else None
    start = datetime.datetime.fromisoformat(start_date).strftime('%Y-%m-%d') if start_date else None
    end = datetime.datetime.fromisoformat(end_date).strftime('%Y-%m-%d') if end_date else None

    dating = Dating.objects.create(
        photo=photo,
        start=start or end,
        end=start or end,
        raw=f'{raw_start}-{raw_end}' if start and end else start and f'{raw_start}' or end and f"-{raw_end}",
        start_accuracy=start_accuracy,
        end_accuracy=end_accuracy,
        start_approximate=start_accuracy != Dating.DAY,
        end_approximate=end_accuracy != Dating.DAY,
        comment='Data from FOTIS / Andmed FOTIS-est'
    )
    photo.dating_count = 1
    photo.first_dating = dating.created
    photo.latest_dating = dating.created
    photo.light_save(update_fields=['dating_count', 'latest_dating'])


def process_single_curator_import_item(item: CuratorImportItem) -> bool:
    profile = item.user
    data = item.data
    upload_form = CuratorPhotoUploadForm(data)

    if not upload_form.is_valid():
        item.status = CuratorImportItem.FAILED
        item.error_message = str(upload_form.errors)
        item.save(update_fields=['status', 'error_message', 'modified'])
        return False

    source_key = upload_form.cleaned_data['identifyingNumber']
    institution = upload_form.cleaned_data.get("institution")
    if institution and institution.split(',')[0] == 'ETERA':
        institution = 'TLÜAR ETERA'
        upload_form.cleaned_data['types'] = 'photo'

    if source_key and ImportBlacklistService().is_blacklisted(source_key):
        item.status = CuratorImportItem.FAILED
        item.error_message = f'Blacklisted: {source_key}'
        item.save(update_fields=['status', 'error_message', 'modified'])
        return False

    licence_obj = _resolve_curator_licence(
        institution,
        upload_form.cleaned_data.get('licence'),
        upload_form.cleaned_data.get('licenceUrl')
    )
    source_id = _resolve_curator_source_id(institution)

    is_digar = upload_form.cleaned_data.get('collections') == 'DIGAR'
    incoming_muis_id = source_key if is_digar else upload_form.cleaned_data['id']
    url_to_record = upload_form.cleaned_data.get('urlToRecord', '')
    muis_id, muis_media_id = _parse_curator_muis_ids(incoming_muis_id, url_to_record, is_digar)

    if is_digar:
        source_key = f'nlib-digar:{upload_form.cleaned_data["identifyingNumber"]}'

    general_albums = Album.objects.filter(id__in=item.album_ids)
    default_album = Album.objects.filter(id=item.auto_album_id).first() if item.auto_album_id else None

    existing_photos = Photo.objects.filter(source_id=source_id, external_id=muis_id)
    existing_photo = existing_photos.filter(external_sub_id=muis_media_id).first() if muis_media_id else existing_photos.first()

    if existing_photo:
        return _handle_curator_existing_photo(item, existing_photo, general_albums, default_album, profile)

    if upload_form.cleaned_data['date'] == '[]':
        upload_form.cleaned_data['date'] = None

    photo_path = None
    try:
        with atomic():
            photo = Photo.objects.create(
                user=profile,
                author=upload_form.cleaned_data['creators'],
                description=upload_form.cleaned_data['title'].rstrip() if upload_form.cleaned_data['title'] else '',
                source_id=source_id,
                types=upload_form.cleaned_data['types'] if upload_form.cleaned_data['types'] else None,
                keywords=upload_form.cleaned_data['keywords'].strip() if upload_form.cleaned_data['keywords'] else None,
                date_text=upload_form.cleaned_data['date'] if upload_form.cleaned_data['date'] else None,
                licence=licence_obj,
                external_id=muis_id,
                external_sub_id=muis_media_id,
                source_key=source_key,
                source_url=upload_form.cleaned_data['urlToRecord'],
                flip=upload_form.cleaned_data['flip'],
                invert=upload_form.cleaned_data['invert'],
                stereo=upload_form.cleaned_data['stereo'],
                rotated=upload_form.cleaned_data['rotated']
            )

            if is_digar:
                photo.image = f'uploads/DIGAR_{str(photo.source_key).split(":")[1]}_1.jpg'
            else:
                _save_photo_image(photo, institution, muis_id, upload_form.cleaned_data['imageUrl'], data.get('_etera_token'))

            photo_path = _apply_photo_transforms(photo)

            lat = upload_form.cleaned_data.get('latitude')
            lng = upload_form.cleaned_data.get('longitude')
            _handle_curator_geotag(photo, lat, lng)

            photo.image
            photo.save()
            photo.add_to_source_album()
            photo.find_similar()

            _link_curator_albums_and_points(photo, general_albums, default_album, profile)
            _link_curator_persons(photo, upload_form.cleaned_data.get('persons', []), lat, lng)
            _link_curator_dating(photo, upload_form)

            item.status = CuratorImportItem.SUCCESS
            item.result_photo = photo
            item.save(update_fields=['status', 'result_photo', 'modified'])
            return True

    except Exception as e:
        ApplicationException.objects.create(exception=traceback.format_exc())
        if photo_path and os.path.exists(photo_path):
            try:
                os.remove(photo_path)
            except OSError:
                pass
        item.status = CuratorImportItem.FAILED
        item.error_message = str(e)
        item.save(update_fields=['status', 'error_message', 'modified'])
        return False


def process_curator_import_queue():
    global _worker_running
    try:
        close_old_connections()
        # Crash recovery: reset stale PROCESSING items (> 10 min) back to PENDING
        stale_cutoff = timezone.now() - datetime.timedelta(minutes=10)
        CuratorImportItem.objects.filter(
            status=CuratorImportItem.PROCESSING,
            modified__lt=stale_cutoff
        ).update(status=CuratorImportItem.PENDING, modified=timezone.now())

        while True:
            item = CuratorImportItem.objects.filter(
                status=CuratorImportItem.PENDING
            ).order_by('id').first()
            if not item:
                break
            rows_updated = CuratorImportItem.objects.filter(
                id=item.id,
                status=CuratorImportItem.PENDING
            ).update(status=CuratorImportItem.PROCESSING, modified=timezone.now())
            if not rows_updated:
                continue

            item.refresh_from_db()
            try:
                process_single_curator_import_item(item)
            except Exception as e:
                try:
                    item.status = CuratorImportItem.FAILED
                    item.error_message = str(e)
                    item.save(update_fields=['status', 'error_message', 'modified'])
                except Exception:
                    pass
            finally:
                close_old_connections()
    finally:
        with _worker_lock:
            if CuratorImportItem.objects.filter(status=CuratorImportItem.PENDING).exists():
                thread = threading.Thread(target=process_curator_import_queue, daemon=True)
                thread.start()
            else:
                _worker_running = False
        close_old_connections()


def start_curator_import_worker():
    global _worker_running
    with _worker_lock:
        if _worker_running:
            return
        _worker_running = True
        thread = threading.Thread(target=process_curator_import_queue, daemon=True)
        thread.start()


def _get_or_create_curator_auto_album(auto_album_id, profile):
    if auto_album_id:
        default_album = Album.objects.filter(pk=auto_album_id, profile=profile, atype=Album.AUTO).first()
        if default_album:
            return default_album
    return Album.objects.create(
        name=f'{str(profile.id)}-{str(timezone.now())}',
        atype=Album.AUTO,
        profile=profile,
        is_public=False,
    )


def _build_curator_import_item(v, etera_token, profile, default_album_pk, album_ids):
    v_copy = dict(v)
    if etera_token:
        v_copy['_etera_token'] = etera_token

    incoming_id = str(v.get('id', ''))
    collections = v.get('collections', '')
    identifying_number = str(v.get('identifyingNumber', ''))
    institution = v.get('institution', '')
    url_to_record = v.get('urlToRecord', '')

    if collections == 'DIGAR':
        incoming_muis_id = identifying_number
        source_desc = 'Rahvusraamatukogu'
    else:
        incoming_muis_id = incoming_id
        source_desc = institution or 'Ajapaik'

    if institution and institution.split(',')[0] == 'ETERA':
        source_desc = 'TLÜAR ETERA'

    if '_' in incoming_muis_id and 'finna.fi' not in url_to_record and 'europeana.eu' not in url_to_record:
        muis_id = incoming_muis_id.split('_')[0]
    else:
        muis_id = incoming_muis_id

    return CuratorImportItem(
        user=profile,
        source_description=source_desc,
        external_id=str(muis_id),
        identifying_number=identifying_number,
        data=v_copy,
        album_ids=album_ids,
        auto_album_id=default_album_pk,
        status=CuratorImportItem.PENDING
    )


@require_POST
def curator_photo_upload_handler(request):
    try:
        user = request.get_user() if hasattr(request, 'get_user') else request.user
        profile = getattr(user, 'profile', None)
    except Exception:
        profile = None

    etera_token = request.POST.get('eteraToken')
    curator_album_selection_form = CuratorWholeSetAlbumsSelectionForm(request.POST)
    selection_json = request.POST.get('selection')

    if not selection_json:
        return JsonResponse({'error': _('Please add pictures to your album')})

    try:
        selection = json.loads(selection_json)
    except Exception:
        return JsonResponse({'error': _('Invalid selection JSON')}, status=400)

    if not selection or not profile or not curator_album_selection_form.is_valid():
        return JsonResponse({'error': _('Not enough data submitted')})

    general_albums = Album.objects.filter(id__in=request.POST.getlist('albums'))
    album_ids = list(general_albums.values_list('id', flat=True))
    default_album = _get_or_create_curator_auto_album(request.POST.get('autoAlbumId'), profile)

    items_to_create = [
        _build_curator_import_item(v, etera_token, profile, default_album.pk, album_ids)
        for v in selection.values()
    ]
    photos_response = {k: {'success': True, 'message': _('OK')} for k in selection.keys()}

    if items_to_create:
        CuratorImportItem.objects.bulk_create(items_to_create)
        start_curator_import_worker()

    return JsonResponse({
        'success': True,
        'queued': len(items_to_create),
        'auto_album_id': default_album.pk,
        'album_id': album_ids[0] if album_ids else None,
        'photos': photos_response,
        'total_points_for_curating': 0
    })


def _clean_curator_import_error(err):
    if not err:
        return ''
    if 'HTTP Error 404: Not Found' in err:
        return _('Photo not found in archive (404)')
    if 'timed out' in err.lower() or 'timeout' in err.lower():
        return _('Archive connection timed out')
    return err


def _format_curator_failed_items(failed_qs):
    failed_items = []
    for fi in failed_qs[:50]:
        data = fi.data or {}
        failed_items.append({
            'id': fi.id,
            'external_id': fi.external_id,
            'reference_code': data.get('identifyingNumber', '') or fi.identifying_number,
            'title': data.get('title', ''),
            'url_to_record': data.get('urlToRecord', ''),
            'error': _clean_curator_import_error(fi.error_message),
            'source': fi.source_description,
            'time': fi.modified.strftime('%H:%M:%S')
        })
    return failed_items


def _recover_stale_curator_import_tasks():
    stale_cutoff = timezone.now() - datetime.timedelta(minutes=10)
    CuratorImportItem.objects.filter(
        status=CuratorImportItem.PROCESSING,
        modified__lt=stale_cutoff
    ).update(status=CuratorImportItem.PENDING, modified=timezone.now())

    if CuratorImportItem.objects.filter(status=CuratorImportItem.PENDING).exists() and not _worker_running:
        start_curator_import_worker()


def curator_import_status(request):
    try:
        user = request.get_user() if hasattr(request, 'get_user') else request.user
        profile = getattr(user, 'profile', None)
    except Exception:
        profile = None

    if not profile:
        return JsonResponse({'active': False, 'pending': 0, 'completed': 0, 'failed': 0, 'failed_items': []})

    if request.method == 'POST' and request.POST.get('action') == 'clear_failed':
        CuratorImportItem.objects.filter(user=profile, status=CuratorImportItem.FAILED).delete()
        return JsonResponse({'success': True})

    _recover_stale_curator_import_tasks()

    pending_count = CuratorImportItem.objects.filter(
        user=profile,
        status__in=[CuratorImportItem.PENDING, CuratorImportItem.PROCESSING]
    ).count()

    recent_since = timezone.now() - datetime.timedelta(hours=24)
    completed_count = CuratorImportItem.objects.filter(
        user=profile,
        status=CuratorImportItem.SUCCESS,
        modified__gte=recent_since
    ).count()

    failed_qs = CuratorImportItem.objects.filter(
        user=profile,
        status=CuratorImportItem.FAILED,
        modified__gte=recent_since
    ).order_by('-modified')

    return JsonResponse({
        'active': pending_count > 0 or _worker_running,
        'pending': pending_count,
        'completed': completed_count,
        'failed': failed_qs.count(),
        'failed_items': _format_curator_failed_items(failed_qs)
    })
