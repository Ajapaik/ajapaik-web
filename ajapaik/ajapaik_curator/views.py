import datetime
import json
import ssl
from urllib.request import build_opener

import requests
from PIL import Image, ImageOps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.db.models import Q, F
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.renderers import JSONRenderer

from ajapaik.ajapaik.forms import CuratorWholeSetAlbumsSelectionForm, CuratorAlbumEditForm, CuratorPhotoUploadForm
from ajapaik.ajapaik.fotis_utils import parse_fotis_timestamp_data
from ajapaik.ajapaik.models import Album, AlbumPhoto, Photo, Licence, Source, GeoTag, Points, Dating
from ajapaik.ajapaik.serializers import CuratorMyAlbumListAlbumSerializer, CuratorAlbumSelectionAlbumSerializer, \
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
    # FIXME: Ugly
    curator_random_image_ids = None
    if last_created_album:
        curator_random_image_ids = AlbumPhoto.objects.filter(
            album_id=last_created_album.id).order_by('?').values_list('photo_id', flat=True)
    if not curator_random_image_ids or curator_random_image_ids.count() < 5:
        curator_random_image_ids = AlbumPhoto.objects.order_by('?').values_list('photo_id', flat=True)
    curator_random_images = Photo.objects.filter(pk__in=curator_random_image_ids)[:5]
    context = {
        'description': _('Search for old photos, add them to Ajapaik, '
                         'determine their locations and share the resulting album!'),
        'curator_random_images': curator_random_images,
        'hostname': request.build_absolute_uri('/'),
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
    serializer = CuratorMyAlbumListAlbumSerializer(
        Album.objects.filter(Q(profile=user_profile, atype__in=[Album.CURATED, Album.PERSON])).order_by('-created'),
        many=True
    )

    return HttpResponse(JSONRenderer().render(serializer.data), content_type='application/json')


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


def curator_photo_upload_handler(request):
    profile = request.get_user().profile

    etera_token = request.POST.get('eteraToken')

    curator_album_selection_form = CuratorWholeSetAlbumsSelectionForm(request.POST)

    selection_json = request.POST.get('selection') or None
    selection = None
    if selection_json is not None:
        selection = json.loads(selection_json)

    all_curating_points = []
    total_points_for_curating = 0
    context = {
        'photos': {}
    }

    if selection and profile is not None and curator_album_selection_form.is_valid():
        general_albums = Album.objects.filter(id__in=request.POST.getlist('albums'))
        if general_albums.exists():
            context['album_id'] = general_albums[0].pk
        else:
            context['album_id'] = None
        default_album = Album(
            name=f'{str(profile.id)}-{str(timezone.now())}',
            atype=Album.AUTO,
            profile=profile,
            is_public=False,
        )
        default_album.save()
        # 15 => unknown copyright
        unknown_licence = Licence.objects.get(pk=15)
        flickr_licence = Licence.objects.filter(url='https://www.flickr.com/commons/usage/').first()
        import_blacklist_service = ImportBlacklistService()

        for k, v in selection.items():
            upload_form = CuratorPhotoUploadForm(v)
            created_album_photo_links = []
            awarded_curator_points = []
            if upload_form.is_valid():
                source_key = upload_form.cleaned_data['identifyingNumber']

                if source_key and import_blacklist_service.is_blacklisted(source_key):
                    context['photos'][k] = {
                        'error': _(
                            f'Could not import picture, as it is blacklisted from being imported: {upload_form.cleaned_data["imageUrl"]}')}
                    context['photos'][k]['success'] = False
                    continue

                if not upload_form.cleaned_data['institution']:
                    licence = unknown_licence
                    source = Source.objects.get(name='AJP')
                else:
                    if upload_form.cleaned_data['institution'] == 'Flickr Commons':
                        licence = flickr_licence
                    else:
                        # For Finna
                        if upload_form.cleaned_data['licence']:
                            licence = Licence.objects.filter(
                                name=upload_form.cleaned_data['licence']).first() or Licence.objects.filter(
                                url=upload_form.cleaned_data['licenceUrl']).first()

                            if not licence:
                                if upload_form.cleaned_data['licence'] != upload_form.cleaned_data['licenceUrl']:
                                    licence_name = upload_form.cleaned_data['licence']
                                else:
                                    licence_name = _get_licence_name_from_url(upload_form.cleaned_data['licenceUrl'])

                                licence = Licence(
                                    name=licence_name,
                                    url=upload_form.cleaned_data['licenceUrl'] or ''
                                )
                                licence.save()
                        else:
                            licence = unknown_licence
                    institution = upload_form.cleaned_data['institution'].split(',')[0]
                    if upload_form.cleaned_data['institution'] == 'ETERA':
                        upload_form.cleaned_data['institution'] = 'TLÜAR ETERA'
                    try:
                        source = Source.objects.get(description=institution)
                    except ObjectDoesNotExist:
                        source = Source.objects.create(name=institution, description=institution)

                existing_photo = None
                if upload_form.cleaned_data['id'] and upload_form.cleaned_data['id'] != '':
                    if upload_form.cleaned_data['collections'] == 'DIGAR':
                        incoming_muis_id = source_key
                    else:
                        incoming_muis_id = upload_form.cleaned_data['id']
                    if 'ETERA' in upload_form.cleaned_data['institution']:
                        upload_form.cleaned_data['types'] = 'photo'
                    if '_' in incoming_muis_id \
                            and not ('finna.fi' in upload_form.cleaned_data['urlToRecord']) \
                            and not ('europeana.eu' in upload_form.cleaned_data['urlToRecord']):
                        muis_id = incoming_muis_id.split('_')[0]
                        muis_media_id = incoming_muis_id.split('_')[1]
                    else:
                        muis_id = incoming_muis_id
                        muis_media_id = None
                    if upload_form.cleaned_data['collections'] == 'DIGAR':
                        source_key = \
                            f'nlib-digar:{upload_form.cleaned_data["identifyingNumber"]}'
                        muis_media_id = 1
                    try:
                        if muis_media_id:
                            existing_photo = Photo.objects.filter(
                                source=source, external_id=muis_id, external_sub_id=muis_media_id).get()
                        else:
                            existing_photo = Photo.objects.filter(
                                source=source, external_id=muis_id).get()
                    except ObjectDoesNotExist:
                        pass
                    if not existing_photo:
                        new_photo = None
                        if upload_form.cleaned_data['date'] == '[]':
                            upload_form.cleaned_data['date'] = None
                        try:
                            new_photo = Photo(
                                user=profile,
                                author=upload_form.cleaned_data['creators'],
                                description=upload_form.cleaned_data['title'].rstrip(),
                                source=source,
                                types=upload_form.cleaned_data['types'] if upload_form.cleaned_data['types'] else None,
                                keywords=upload_form.cleaned_data['keywords'].strip() if upload_form.cleaned_data[
                                    'keywords'] else None,
                                date_text=upload_form.cleaned_data['date'] if upload_form.cleaned_data[
                                    'date'] else None,
                                licence=licence,
                                external_id=muis_id,
                                external_sub_id=muis_media_id,
                                source_key=source_key,
                                source_url=upload_form.cleaned_data['urlToRecord'],
                                flip=upload_form.cleaned_data['flip'],
                                invert=upload_form.cleaned_data['invert'],
                                stereo=upload_form.cleaned_data['stereo'],
                                rotated=upload_form.cleaned_data['rotated']
                            )
                            new_photo.save()
                            if upload_form.cleaned_data['collections'] == 'DIGAR':
                                new_photo.image = f'uploads/DIGAR_{str(new_photo.source_key).split(":")[1]}_1.jpg'
                            else:
                                # Enable plain http and broken SSL
                                ssl._create_default_https_context = ssl._create_unverified_context
                                opener = build_opener()
                                headers = [('User-Agent', settings.UA)]
                                if etera_token:
                                    headers.append(('Authorization', f'Bearer {etera_token}'))
                                opener.addheaders = headers
                                img_response = opener.open(upload_form.cleaned_data['imageUrl'])
                                if 'ETERA' in new_photo.source.description:
                                    img = ContentFile(img_response.read())
                                    new_photo.image_no_watermark.save('etera.jpg', img)
                                    new_photo.watermark()
                                else:
                                    new_photo.image.save('muis.jpg', ContentFile(img_response.read()))
                            if new_photo.invert:
                                photo_path = f'{settings.MEDIA_ROOT}/{str(new_photo.image)}'
                                img = Image.open(photo_path)
                                inverted_grayscale_image = ImageOps.invert(img).convert('L')
                                inverted_grayscale_image.save(photo_path)
                            if new_photo.rotated is not None and new_photo.rotated > 0:
                                photo_path = f'{settings.MEDIA_ROOT}/{str(new_photo.image)}'
                                img = Image.open(photo_path)
                                rot = img.rotate(new_photo.rotated, expand=1)
                                rot.save(photo_path)
                                new_photo.width, new_photo.height = rot.size
                            if new_photo.flip:
                                photo_path = f'{settings.MEDIA_ROOT}/{str(new_photo.image)}'
                                img = Image.open(photo_path)
                                flipped_image = img.transpose(Image.FLIP_LEFT_RIGHT)
                                flipped_image.save(photo_path)
                            context['photos'][k] = {}
                            context['photos'][k]['message'] = _('OK')

                            lat = upload_form.cleaned_data.get('latitude')
                            lng = upload_form.cleaned_data.get('longitude')

                            gt_exists = GeoTag.objects.filter(type=GeoTag.SOURCE_GEOTAG,
                                                              photo__source_key=new_photo.source_key).exists()
                            if lat and lng and not gt_exists:
                                source_geotag = GeoTag(
                                    lat=lat,
                                    lon=lng,
                                    origin=GeoTag.SOURCE,
                                    type=GeoTag.SOURCE_GEOTAG,
                                    map_type=GeoTag.NO_MAP,
                                    photo=new_photo,
                                    is_correct=True,
                                    trustworthiness=0.07
                                )
                                source_geotag.save()
                                new_photo.latest_geotag = source_geotag.created
                                new_photo.set_calculated_fields()
                            new_photo.image
                            new_photo.save()
                            new_photo.set_aspect_ratio()
                            new_photo.add_to_source_album()
                            new_photo.find_similar()
                            points_for_curating = Points(action=Points.PHOTO_CURATION, photo=new_photo, points=50,
                                                         user=profile, created=new_photo.created,
                                                         album=general_albums[0])
                            points_for_curating.save()
                            awarded_curator_points.append(points_for_curating)
                            if general_albums.exists():
                                for a in general_albums:
                                    ap = AlbumPhoto(photo=new_photo, album=a, profile=profile, type=AlbumPhoto.CURATED)
                                    ap.save()
                                    created_album_photo_links.append(ap)
                                    if not a.cover_photo:
                                        a.cover_photo = new_photo
                                        a.light_save()
                                for b in general_albums[1:]:
                                    points_for_curating = Points(action=Points.PHOTO_RECURATION, photo=new_photo,
                                                                 points=30,
                                                                 user=profile, created=new_photo.created,
                                                                 album=b)
                                    points_for_curating.save()
                                    awarded_curator_points.append(points_for_curating)
                                    all_curating_points.append(points_for_curating)
                            ap = AlbumPhoto(photo=new_photo, album=default_album, profile=profile,
                                            type=AlbumPhoto.CURATED)
                            ap.save()
                            created_album_photo_links.append(ap)

                            persons = upload_form.cleaned_data.get('persons', [])

                            if persons:
                                existing_albums = Album.objects.filter(name__in=persons, atype=Album.PERSON)
                                album_ids = list(existing_albums.values_list('id', flat=True))

                                for album in existing_albums:
                                    person_ap = AlbumPhoto.objects.create(
                                        photo=new_photo,
                                        album=album,
                                        type=AlbumPhoto.FACE_TAGGED
                                    )
                                    created_album_photo_links.append(person_ap)

                                existing_names = existing_albums.values_list('name', flat=True)
                                new_names = list(set(persons) - set(existing_names))

                                for person_name in new_names:
                                    album = Album.objects.create(
                                        name=person_name,
                                        atype=Album.PERSON,
                                    )
                                    album_ids.append(album.id)
                                    person_ap = AlbumPhoto.objects.create(
                                        photo=new_photo,
                                        album=album,
                                        type=AlbumPhoto.FACE_TAGGED
                                    )
                                    created_album_photo_links.append(person_ap)

                                affected_albums = Album.objects.filter(id__in=album_ids)
                                affected_albums.update(photo_count_with_subalbums=F('photo_count_with_subalbums') + 1)

                                if lat and lng:
                                    affected_albums.update(
                                        geotagged_photo_count_with_subalbums=F(
                                            'geotagged_photo_count_with_subalbums') + 1)

                                affected_albums_without_photo = affected_albums.filter(cover_photo=None)
                                affected_albums_without_photo.update(cover_photo=new_photo)

                            start_date = upload_form.cleaned_data.get('start_date')
                            end_date = upload_form.cleaned_data.get('end_date')

                            if start_date or end_date:
                                date_start_accuracy = upload_form.cleaned_data.get('date_start_accuracy')
                                date_end_accuracy = upload_form.cleaned_data.get('date_end_accuracy')

                                start_accuracy, raw_start_pattern = parse_fotis_timestamp_data(date_start_accuracy)
                                end_accuracy, raw_end_pattern = parse_fotis_timestamp_data(date_end_accuracy)

                                raw_start = datetime.datetime.fromisoformat(start_date).strftime(
                                    raw_start_pattern) if start_date else None
                                raw_end = datetime.datetime.fromisoformat(end_date).strftime(
                                    raw_end_pattern) if end_date else None

                                start = datetime.datetime.fromisoformat(start_date).strftime(
                                    '%Y-%m-%d') if start_date else None

                                end = datetime.datetime.fromisoformat(end_date).strftime(
                                    '%Y-%m-%d') if end_date else None

                                dating = Dating.objects.create(
                                    photo=new_photo,
                                    start=start or end,
                                    end=start or end,
                                    raw=f'{raw_start}-{raw_end}' if start and end else start and f'{raw_start}' or end and f"-{raw_end}",
                                    start_accuracy=start_accuracy,
                                    end_accuracy=end_accuracy,
                                    start_approximate=start_accuracy != Dating.DAY,
                                    end_approximate=end_accuracy != Dating.DAY,
                                    comment=f'Data from FOTIS / Andmed FOTIS-est'
                                )

                                new_photo.dating_count = 1
                                new_photo.first_dating = dating.created
                                new_photo.latest_dating = dating.created
                                new_photo.light_save(update_fields=['dating_count', 'latest_dating', 'dating_count'])

                            context['photos'][k]['success'] = True
                            all_curating_points.append(points_for_curating)
                        except Exception as e:
                            if new_photo:
                                new_photo.image.delete()
                                new_photo.delete()
                            for ap in created_album_photo_links:
                                ap.delete()
                            for cp in awarded_curator_points:
                                cp.delete()
                            context['photos'][k] = {'error': _('Error uploading file: %s (%s)' %
                                                               (e, upload_form.cleaned_data['imageUrl']))}
                    else:
                        if general_albums.exists():
                            for a in general_albums:
                                ap = AlbumPhoto(photo=existing_photo, album=a, profile=profile,
                                                type=AlbumPhoto.RECURATED)
                                ap.save()
                                points_for_recurating = Points(user=profile, action=Points.PHOTO_RECURATION,
                                                               photo=existing_photo, points=30,
                                                               album=general_albums[0], created=timezone.now())
                                points_for_recurating.save()
                                all_curating_points.append(points_for_recurating)
                        dap = AlbumPhoto(photo=existing_photo, album=default_album, profile=profile,
                                         type=AlbumPhoto.RECURATED)
                        dap.save()
                        context['photos'][k] = {}
                        context['photos'][k]['success'] = True
                        context['photos'][k]['message'] = _('Photo already exists in Ajapaik')
            else:
                context['photos'][k] = {}
                context['photos'][k]['error'] = _('Error uploading file: %s (%s)'
                                                  % (upload_form.errors, upload_form.cleaned_data['imageUrl']))

        if general_albums:
            game_reverse = request.build_absolute_uri(reverse('game'))
            for ga in general_albums:
                requests.post(
                    f'https://graph.facebook.com/v7.0/?id={game_reverse}?album={str(ga.id)}&scrape=true'
                )
        for cp in all_curating_points:
            total_points_for_curating += cp.points
        context['total_points_for_curating'] = total_points_for_curating
        if general_albums.exists():
            for album in general_albums:
                album.save()
                if album.subalbum_of:
                    album.subalbum_of.save()
    else:
        if not selection or len(selection) == 0:
            error = _('Please add pictures to your album')
        else:
            error = _('Not enough data submitted')
        context = {
            'error': error
        }
    return HttpResponse(json.dumps(context), content_type='application/json')
