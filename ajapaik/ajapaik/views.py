# encoding: utf-8
import json
import logging
import urllib
from math import ceil
from time import time
from urllib.request import build_opener
from xml.etree import ElementTree as ET

from PIL import Image, ImageFile
from django.conf import settings
from django.contrib.gis.db.models.functions import GeometryDistance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Q, Count, F, Min, Max
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import condition
from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet
from rest_framework.renderers import JSONRenderer
from sorl.thumbnail import delete
from sorl.thumbnail import get_thumbnail

from ajapaik.ajapaik.forms import AddAlbumForm, AreaSelectionForm, AlbumSelectionForm, AddAreaForm, \
    GameAlbumSelectionForm, GameNextPhotoForm, MapDataRequestForm, GalleryFilteringForm, \
    PhotoSelectionForm, SelectionUploadForm, AlbumInfoModalForm, PhotoLikeForm, \
    AlbumSelectionFilteringForm, CuratorWholeSetAlbumsSelectionForm
from ajapaik.ajapaik.models import Photo, GeoTag, Points, \
    Album, AlbumPhoto, Area, Licence, \
    MuisCollection, PhotoLike, ImageSimilarity, get_pseudo_slug_for_photo, Dating
from ajapaik.ajapaik.serializers import FrontpageAlbumSerializer, DatingSerializer, \
    VideoSerializer, PhotoMapMarkerSerializer
from ajapaik.ajapaik.stats_sql import AlbumStats
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle
from ajapaik.utils import get_etag, calculate_thumbnail_size, calculate_thumbnail_size_max_height, \
    last_modified
from .utils import get_pagination_parameters, is_ajax

log = logging.getLogger(__name__)

Image.MAX_IMAGE_PIXELS = 933120000
ImageFile.LOAD_TRUNCATED_IMAGES = True


def image_thumb(request, photo_id=None, thumb_size=400, pseudo_slug=None):
    if thumb_size <= 400:
        thumb_size = 400
    else:
        thumb_size = 1024

    p = get_object_or_404(Photo, id=photo_id)
    thumb_str = f'{str(thumb_size)}x{str(thumb_size)}'

    if p.rephoto_of:
        original_thumb = get_thumbnail(p.rephoto_of.image, thumb_str, upscale=False)
        thumb_str = f'{str(original_thumb.size[0])}x{str(original_thumb.size[1])}'
        # TODO: see if restricting Pillow version fixes this
        im = get_thumbnail(p.image, thumb_str, upscale=True, downscale=True, crop='center')
    else:
        im = get_thumbnail(p.image, thumb_str, upscale=False)

    try:
        content = im.read()
    except IOError:
        delete(im)
        im = get_thumbnail(p.image, thumb_str, upscale=False)
        content = im.read()

    return get_image_thumb(request, f'{settings.MEDIA_ROOT}/{im.name}', content)


@condition(etag_func=get_etag, last_modified_func=last_modified)
@cache_control(must_revalidate=True)
def get_image_thumb(request, image, content):
    return HttpResponse(content, content_type='image/jpg')


@cache_control(max_age=604800)
def image_full(request, photo_id=None, pseudo_slug=None):
    p = get_object_or_404(Photo, id=photo_id)
    content = p.image.read()

    return HttpResponse(content, content_type='image/jpg')


def get_general_info_modal_content(request):
    profile = request.get_user().profile
    photo_qs = Photo.objects.filter(rephoto_of__isnull=True)
    rephoto_qs = Photo.objects.filter(rephoto_of__isnull=False)
    geotags_qs = GeoTag.objects.filter()
    cached_data = cache.get('general_info_modal_cache', None)
    person_annotation_qs = FaceRecognitionRectangle.objects.filter(deleted=None)
    person_annotation_with_person_album_qs = person_annotation_qs.exclude(subject_consensus=None)
    person_annotation_with_subject_data_qs = person_annotation_qs.exclude(Q(gender=None) & Q(age=None))

    if cached_data is None:
        cached_data = {
            'photos_count': photo_qs.count(),
            'contributing_users_count': geotags_qs.distinct('user').count(),
            'photos_geotagged_count': photo_qs.filter(lat__isnull=False, lon__isnull=False).count(),
            'rephotos_count': rephoto_qs.count(),
            'rephotographing_users_count': rephoto_qs.order_by('user').distinct('user').count(),
            'photos_with_rephotos_count': rephoto_qs.order_by('rephoto_of_id').distinct('rephoto_of_id').count(),
            'person_annotation_count': person_annotation_qs.count(),
            'person_annotation_count_with_person_album': person_annotation_with_person_album_qs.count(),
            'person_annotation_count_with_subject_data': person_annotation_with_subject_data_qs.count()
        }
        cache.set('general_info_modal_cache', cached_data, settings.GENERAL_INFO_MODAL_CACHE_TTL)
    context = {
        'user': request.get_user(),
        'total_photo_count': cached_data['photos_count'],
        'contributing_users': cached_data['contributing_users_count'],
        'total_photos_tagged': cached_data['photos_geotagged_count'],
        'rephoto_count': cached_data['rephotos_count'],
        'rephotographing_users': cached_data['rephotographing_users_count'],
        'rephotographed_photo_count': cached_data['photos_with_rephotos_count'],
        'person_annotation_count': cached_data['person_annotation_count'],
        'person_annotation_count_with_person_album': cached_data['person_annotation_count_with_person_album'],
        'person_annotation_count_with_subject_data': cached_data['person_annotation_count_with_subject_data'],
    }

    return render(request, 'info/_general_info_modal_content.html', context)


# 2022-11-02 faster rewrite of get_album_info_modal_content() query
# number of rephoto_user_count and geotagging_user_count is 1 smaller
# than old because different way to handle NULL:s

def get_album_info_modal_content(request):
    starttime = time()

    profile = request.get_user().profile
    form = AlbumInfoModalForm(request.GET)
    if form.is_valid():
        album = form.cleaned_data['album']
        context = {'album': album, 'link_to_map': form.cleaned_data['linkToMap'],
                   'link_to_game': form.cleaned_data['linkToGame'],
                   'link_to_gallery': form.cleaned_data['linkToGallery'],
                   'fb_share_game': form.cleaned_data['fbShareGame'], 'fb_share_map': form.cleaned_data['fbShareMap'],
                   'fb_share_gallery': form.cleaned_data['fbShareGallery'],
                   'total_photo_count': album.photo_count_with_subalbums or 0,
                   'geotagged_photo_count': album.geotagged_photo_count_with_subalbums}

        subalbums = [album.id]
        for sa in album.subalbums.filter(atype__in=[Album.CURATED, Album.PERSON]):
            subalbums.append(sa.id)

        rephotostats = AlbumStats.get_rephoto_stats_sql(subalbums, profile.pk)

        context['user_geotagged_photo_count'] = AlbumStats.get_user_geotagged_photo_count_sql(subalbums, profile.pk)
        context['geotagging_user_count'] = AlbumStats.get_geotagging_user_count_sql(subalbums)
        context['rephoto_count'] = rephotostats["rephoto_count"]
        context['rephoto_user_count'] = rephotostats["rephoto_user_count"]
        context['rephotographed_photo_count'] = rephotostats["rephotographed_photo_count"]
        context['user_rephoto_count'] = rephotostats["user_rephoto_count"]
        context['user_rephotographed_photo_count'] = rephotostats["user_rephotographed_photo_count"]
        context['user_made_all_rephotos'] = rephotostats['user_made_all_rephotos']
        context['similar_photo_count'] = album.similar_photo_count_with_subalbums
        context['confirmed_similar_photo_count'] = album.confirmed_similar_photo_count_with_subalbums
        context['album_curators'] = AlbumStats.get_album_curators_sql([album.id])

        if album.lat and album.lon:
            ref_location = Point(x=album.lon, y=album.lat, srid=4326)
            context['nearby_albums'] = Album.objects \
                                           .filter(
                geography__dwithin=(ref_location, D(m=5000)),
                is_public=True,
                atype=Album.CURATED,
                id__ne=album.id
            ).order_by('?')[:3]

        album_id_str = str(album.id)
        context['share_game_link'] = f'{request.build_absolute_uri(reverse("game"))}?album={album_id_str}'
        context['share_map_link'] = f'{request.build_absolute_uri(reverse("map"))}?album={album_id_str}'
        context['share_gallery_link'] = f'{request.build_absolute_uri(reverse("frontpage"))}?album={album_id_str}'
        context['execution_time'] = starttime - time()

        return render(request, 'info/_info_modal_content.html', context)

    return HttpResponse('Error')


def _get_album_choices(qs=None, start=None, end=None):
    # TODO: Sort out
    if qs != None and qs.exists():
        albums = qs.prefetch_related('cover_photo').order_by('-created')[start:end]
    else:
        albums = Album.objects.filter(is_public=True).prefetch_related('cover_photo').order_by('-created')[start:end]
    for a in albums:
        if a.cover_photo:
            a.cover_photo_width, a.cover_photo_height = calculate_thumbnail_size(a.cover_photo.width,
                                                                                 a.cover_photo.height, 400)
        else:
            a.cover_photo_width, a.cover_photo_height = 400, 300

    return albums


def fetch_stream(request):
    profile = request.get_user().profile
    form = GameNextPhotoForm(request.GET)
    data = {'photo': None, 'userSeenAll': False, 'nothingMoreToShow': False}
    if form.is_valid():
        qs = Photo.objects.filter(rephoto_of__isnull=True)
        form_area = form.cleaned_data['area']
        form_album = form.cleaned_data['album']
        form_photo = form.cleaned_data['photo']
        # TODO: Correct implementation
        if form_photo:
            form_photo.user_already_confirmed = False
            last_confirm_geotag_by_this_user_for_photo = form_photo.geotags.filter(user_id=profile.id,
                                                                                   type=GeoTag.CONFIRMATION).order_by(
                '-created').first()
            if last_confirm_geotag_by_this_user_for_photo and (
                    form_photo.lat == last_confirm_geotag_by_this_user_for_photo.lat
                    and form_photo.lon == last_confirm_geotag_by_this_user_for_photo.lon):
                form_photo.user_already_confirmed = True
            form_photo.user_already_geotagged = form_photo.geotags.filter(user_id=profile.id).exists()
            form_photo.user_likes = PhotoLike.objects.filter(profile=profile, photo=form_photo, level=1).exists()
            form_photo.user_loves = PhotoLike.objects.filter(profile=profile, photo=form_photo, level=2).exists()
            form_photo.user_like_count = PhotoLike.objects.filter(photo=form_photo).distinct('profile').count()
            data = {'photo': Photo.get_game_json_format_photo(form_photo), 'userSeenAll': False,
                    'nothingMoreToShow': False}
        else:
            if form_album:
                # TODO: Could be done later where we're frying our brains with nextPhoto logic anyway
                photos_ids_in_album = list(form_album.photos.values_list('id', flat=True))
                subalbums = form_album.subalbums.exclude(atype=Album.AUTO)
                for sa in subalbums:
                    photos_ids_in_subalbum = list(sa.photos.values_list('id', flat=True))
                    photos_ids_in_album += photos_ids_in_subalbum
                qs = qs.filter(pk__in=photos_ids_in_album)
            elif form_area:
                qs = qs.filter(area=form_area)
            # FIXME: Ugly
            try:
                response = Photo.get_next_photo_to_geotag(qs, request)
                data = {'photo': response[0], 'userSeenAll': response[1], 'nothingMoreToShow': response[2]}
            except IndexError:
                pass

    return HttpResponse(json.dumps(data), content_type='application/json')


# Params for old URL support
def frontpage(request, album_id=None, page=None):
    profile = request.get_user().profile
    data = _get_filtered_data_for_frontpage(request, album_id, page)

    user_has_likes = profile.likes.exists()
    user_has_rephotos = profile.photos.filter(rephoto_of__isnull=False).exists()

    if data['rephotos_by_name']:
        title = _('%(name)s - rephotos') % {'name': data['rephotos_by_name']}
    elif data['album']:
        title = data['album'][1]
    else:
        title = ''

    # Using "nulls last" here as it uses same index
    # which is already used in _get_filtered_data_for_frontpage()
    last_geotagged_photo = Photo.objects.order_by(F('latest_geotag').desc(nulls_last=True)).first()
    filters = ['film', 'collections', 'people', 'backsides', 'exteriors', 'interiors',
               'portrait', 'square', 'landscape', 'panoramic', 'ground_viewpoint_elevation',
               'raised_viewpoint_elevation', 'aerial_viewpoint_elevation', 'no_geotags', 'high_quality'
               ]
    highlight_filter_icon = (data['order2'] != 'added' or data['order3'] == 'reverse') or \
                            len([filter for filter in filters if filter in request.GET]) > 0
    context = {
        'is_frontpage': True,
        'title': title,
        'hostname': request.build_absolute_uri('/'),
        'ajapaik_facebook_link': settings.AJAPAIK_FACEBOOK_LINK,
        'facebook_share_photos': data['fb_share_photos'],
        'album': data['album'],
        'photo': data['photo'],
        'page': data['page'],
        'order1': data['order1'],
        'order2': data['order2'],
        'order3': data['order3'],
        'user_has_likes': user_has_likes,
        'user_has_rephotos': user_has_rephotos,
        'my_likes_only': data['my_likes_only'],
        'rephotos_by': data['rephotos_by'],
        'rephotos_by_name': data['rephotos_by_name'],
        'photos_with_comments': data['photos_with_comments'],
        'photos_with_rephotos': data['photos_with_rephotos'],
        'photos_with_similar_photos': data['photos_with_similar_photos'],
        'show_photos': data['show_photos'],
        'is_photoset': data['is_photoset'],
        'last_geotagged_photo_id': last_geotagged_photo.id if last_geotagged_photo else None,
        'highlight_filter_icon': highlight_filter_icon
    }

    return render(request, 'common/frontpage.html', context)


def frontpage_async_data(request):
    data = _get_filtered_data_for_frontpage(request)
    data['fb_share_photos'] = None

    return HttpResponse(json.dumps(data), content_type='application/json')


def frontpage_async_albums(request):
    form = AlbumSelectionFilteringForm(request.GET)
    context = {}
    if form.is_valid():
        page = form.cleaned_data['page']
        if page is None:
            page = 1
        page_size = settings.FRONTPAGE_DEFAULT_ALBUM_PAGE_SIZE
        start = (page - 1) * page_size
        albums = Album.objects
        if form.cleaned_data['people']:
            albums = albums.filter(cover_photo__isnull=False, atype=Album.PERSON)
        if form.cleaned_data['collections']:
            albums = albums.filter(atype=Album.COLLECTION, cover_photo__isnull=False, is_public=True)
        if form.cleaned_data['film']:
            albums = albums.filter(is_film_still_album=True, cover_photo__isnull=False, is_public=True)
        if albums == Album.objects:
            albums = albums.exclude(atype__in=[Album.AUTO, Album.FAVORITES]).filter(
                cover_photo__isnull=False,
                is_public=True
            )
        q = form.cleaned_data['q']
        if q:
            sqs = SearchQuerySet().models(Album).filter(content=AutoQuery(q))
            albums = albums.filter(pk__in=[r.pk for r in sqs])
        total = albums.count()
        if start < 0:
            start = 0
        if start > total:
            start = total
        if int(start + page_size) > total:
            end = total
        else:
            end = start + page_size
        end = int(end)
        max_page = int(ceil(float(total) / float(page_size)))

        albums = _get_album_choices(albums, start, end)
        serializer = FrontpageAlbumSerializer(albums, many=True)
        context['start'] = start
        context['end'] = end
        context['total'] = total
        context['max_page'] = max_page
        context['page'] = page
        context['albums'] = serializer.data
    return HttpResponse(json.dumps(context), content_type='application/json')


def _get_filtered_data_for_frontpage(request, album_id=None, page_override=None):
    start_time = time()
    profile = request.get_user().profile
    photos = Photo.objects.filter(rephoto_of__isnull=True)
    filter_form = GalleryFilteringForm(request.GET)
    page_size = settings.FRONTPAGE_DEFAULT_PAGE_SIZE
    context = {}
    if filter_form.is_valid():
        if album_id:
            album = Album.objects.get(pk=album_id)
        else:
            album = filter_form.cleaned_data['album']
        requested_photo = filter_form.cleaned_data['photo']
        requested_photos = filter_form.cleaned_data['photos']
        order1 = filter_form.cleaned_data['order1']
        order2 = filter_form.cleaned_data['order2']
        order3 = filter_form.cleaned_data['order3']
        default_ordering = False
        if not order1 and not order2:
            order1 = 'time'
            order2 = 'added'
            default_ordering = True
        context['order1'] = order1
        context['order2'] = order2
        context['order3'] = order3
        my_likes_only = filter_form.cleaned_data['myLikes']
        rephotos_by_name = None
        rephotos_by_id = None
        if filter_form.cleaned_data['rephotosBy']:
            rephotos_by_name = filter_form.cleaned_data['rephotosBy'].get_display_name
            rephotos_by_id = filter_form.cleaned_data['rephotosBy'].pk
            rephotos_by = filter_form.cleaned_data['rephotosBy']
        else:
            rephotos_by = None
        if not album and not requested_photos and not my_likes_only and not rephotos_by \
                and not filter_form.cleaned_data['order1']:
            context['fb_share_photos'] = None
            context['facebook_share_photos'] = None
            context['album'] = None
            context['photo'] = None
            context['page'] = None
            context['user_has_likes'] = None
            context['user_has_rephotos'] = None
            context['my_likes_only'] = None
            context['rephotos_by'] = rephotos_by_id or None
            context['rephotos_by_name'] = rephotos_by_name or None
            context['photos_with_comments'] = None
            context['photos_with_rephotos'] = None
            context['photos_with_similar_photos'] = None
            context['show_photos'] = None
            context['is_photoset'] = None
            context['execution_time'] = str(time() - start_time)
            return context
        else:
            show_photos = True
        lat = filter_form.cleaned_data['lat']
        lon = filter_form.cleaned_data['lon']
        if page_override:
            page = int(page_override)
        else:
            page = filter_form.cleaned_data['page']

        # Do not show hidden photos
        if not album or album.id != 38516:
            blacklist_exists = Album.objects.filter(id=38516).exists()
            if blacklist_exists:
                photos = photos.exclude(albums__in=[38516])

        # FILTERING BELOW THIS LINE

        if album:
            sa_ids = [album.id]
            for sa in album.subalbums.exclude(atype=Album.AUTO):
                sa_ids.append(sa.id)
            photos = photos.filter(albums__in=sa_ids)

            # In QuerySet "albums__in" is 1:M JOIN  so images will show up
            # multiple times in results so this needs to be distinct(). Distinct is slow.
            photos = photos.distinct()

        date_from = filter_form.cleaned_data["date_from"]
        date_to = filter_form.cleaned_data["date_to"]
        if date_from or date_to:
            photos = photos.exclude(datings=None).select_related("datings")

        if filter_form.cleaned_data['people']:
            photos = photos.filter(face_recognition_rectangles__isnull=False,
                                   face_recognition_rectangles__deleted__isnull=True)
        if filter_form.cleaned_data['backsides']:
            photos = photos.filter(front_of__isnull=False)
        if filter_form.cleaned_data['interiors']:
            photos = photos.filter(scene=0)
        if filter_form.cleaned_data['exteriors']:
            photos = photos.exclude(scene=0)
        if filter_form.cleaned_data['ground_viewpoint_elevation']:
            photos = photos.exclude(viewpoint_elevation=1).exclude(viewpoint_elevation=2)
        if filter_form.cleaned_data['raised_viewpoint_elevation']:
            photos = photos.filter(viewpoint_elevation=1)
        if filter_form.cleaned_data['aerial_viewpoint_elevation']:
            photos = photos.filter(viewpoint_elevation=2)
        if filter_form.cleaned_data['no_geotags']:
            photos = photos.filter(geotag_count=0)
        if filter_form.cleaned_data['high_quality']:
            photos = photos.filter(height__gte=1080)
        if filter_form.cleaned_data['portrait']:
            photos = photos.filter(aspect_ratio__lt=0.95)
        if filter_form.cleaned_data['square']:
            photos = photos.filter(aspect_ratio__gte=0.95, aspect_ratio__lt=1.05)
        if filter_form.cleaned_data['landscape']:
            photos = photos.filter(aspect_ratio__gte=1.05, aspect_ratio__lt=2.0)
        if filter_form.cleaned_data['panoramic']:
            photos = photos.filter(aspect_ratio__gte=2.0)
        if requested_photos:
            requested_photos = requested_photos.split(',')
            context['is_photoset'] = True
            photos = photos.filter(id__in=requested_photos)
        else:
            context['is_photoset'] = False
        if my_likes_only:
            photos = photos.filter(likes__profile=profile)
        if rephotos_by_id:
            photos = photos.filter(rephotos__user_id=rephotos_by_id)

        if date_from or date_to:
            datings = Dating.objects.filter(photo_id__in=photos.values_list("id", flat=True))

            if date_from:
                datings = datings.filter(start__gte=date_from)

            if date_to:
                datings = datings.filter(end__lte=date_to)

            photos = photos.filter(id__in=datings.values_list("photo_id", flat=True))

        photos_with_comments = None
        photos_with_rephotos = None
        photos_with_similar_photos = None
        q = filter_form.cleaned_data['q']
        if q and show_photos:
            sqs = SearchQuerySet().models(Photo).filter(content=AutoQuery(q))
            photos = photos.filter(pk__in=[r.pk for r in sqs], rephoto_of__isnull=True)

        # In some cases it is faster to get number of photos before we annotate new columns to it
        albumsize_before_sorting = 0
        if not album:
            albumsize_before_sorting = Photo.objects.filter(pk__in=photos).cached_count(str(filter_form.cleaned_data))

        # SORTING BELOW THIS LINE

        if order1 == 'closest' and lat and lon:
            ref_location = Point(x=lon, y=lat, srid=4326)
            if order3 == 'reverse':
                photos = photos.annotate(distance=GeometryDistance(('geography'), ref_location)).order_by('-distance')
            else:
                photos = photos.annotate(distance=GeometryDistance(('geography'), ref_location)).order_by('distance')
        elif order1 == 'amount':
            if order2 == 'comments':
                if order3 == 'reverse':
                    photos = photos.order_by('comment_count')
                else:
                    photos = photos.order_by('-comment_count')
                photos_with_comments = photos.filter(comment_count__gt=0).count()
            elif order2 == 'rephotos':
                if order3 == 'reverse':
                    photos = photos.order_by('rephoto_count')
                else:
                    photos = photos.order_by('-rephoto_count')
                photos_with_rephotos = photos.filter(rephoto_count__gt=0).count()
            elif order2 == 'geotags':
                if order3 == 'reverse':
                    photos = photos.order_by('geotag_count')
                else:
                    photos = photos.order_by('-geotag_count')
            elif order2 == 'likes':
                if order3 == 'reverse':
                    photos = photos.order_by('like_count')
                else:
                    photos = photos.order_by('-like_count')
            elif order2 == 'views':
                if order3 == 'reverse':
                    photos = photos.order_by('view_count')
                else:
                    photos = photos.order_by('-view_count')
            elif order2 == 'datings':
                if order3 == 'reverse':
                    photos = photos.order_by('dating_count')
                else:
                    photos = photos.order_by('-dating_count')
            elif order2 == 'transcriptions':
                if order3 == 'reverse':
                    photos = photos.order_by('transcription_count')
                else:
                    photos = photos.order_by('-transcription_count')
            elif order2 == 'annotations':
                if order3 == 'reverse':
                    photos = photos.order_by('annotation_count')
                else:
                    photos = photos.order_by('-annotation_count')
            elif order2 == 'similar_photos':
                photos = photos.annotate(similar_photo_count=Count('similar_photos', distinct=True))
                if order3 == 'reverse':
                    photos = photos.order_by('similar_photo_count')
                else:
                    photos = photos.order_by('-similar_photo_count')
        elif order1 == 'time':
            if order2 == 'rephotos':
                if order3 == 'reverse':
                    photos = photos.order_by(F('first_rephoto').asc(nulls_last=True))
                else:
                    photos = photos.order_by(F('latest_rephoto').desc(nulls_last=True))
                photos_with_rephotos = photos.filter(first_rephoto__isnull=False).count()
            elif order2 == 'comments':
                if order3 == 'reverse':
                    photos = photos.order_by(F('first_comment').asc(nulls_last=True))
                else:
                    photos = photos.order_by(F('latest_comment').desc(nulls_last=True))
                photos_with_comments = photos.filter(comment_count__gt=0).count()
            elif order2 == 'geotags':
                if order3 == 'reverse':
                    photos = photos.order_by(F('first_geotag').asc(nulls_last=True))
                else:
                    photos = photos.order_by(F('latest_geotag').desc(nulls_last=True))
            elif order2 == 'likes':
                if order3 == 'reverse':
                    photos = photos.order_by(F('first_like').asc(nulls_last=True))
                else:
                    photos = photos.order_by(F('latest_like').desc(nulls_last=True))
            elif order2 == 'views':
                if order3 == 'reverse':
                    photos = photos.order_by(F('first_view').asc(nulls_last=True))
                else:
                    photos = photos.order_by(F('latest_view').desc(nulls_last=True))
            elif order2 == 'datings':
                if order3 == 'reverse':
                    photos = photos.order_by(F('first_dating').asc(nulls_last=True))
                else:
                    photos = photos.order_by(F('latest_dating').desc(nulls_last=True))
            elif order2 == 'transcriptions':
                if order3 == 'reverse':
                    photos = photos.order_by(F('first_transcription').asc(nulls_last=True))
                else:
                    photos = photos.order_by(F('latest_transcription').desc(nulls_last=True))
            elif order2 == 'annotations':
                if order3 == 'reverse':
                    photos = photos.order_by(F('first_annotation').asc(nulls_last=True))
                else:
                    photos = photos.order_by(F('latest_annotation').desc(nulls_last=True))
            elif order2 == 'stills':
                if order3 == 'reverse':
                    photos = photos.order_by('-video_timestamp')
                else:
                    photos = photos.order_by('video_timestamp')
            elif order2 == 'added':
                if order3 == 'reverse':
                    photos = photos.order_by('id')
                else:
                    photos = photos.order_by('-id')
                if order1 == 'time':
                    default_ordering = True
            elif order2 == 'similar_photos':
                photos = photos.annotate(similar_photo_count=Count('similar_photos', distinct=True))
                if order3 == 'reverse':
                    photos = photos.order_by('similar_photo_count')
                else:
                    photos = photos.order_by('-similar_photo_count')
        else:
            if order3 == 'reverse':
                photos = photos.order_by('id')
            else:
                photos = photos.order_by('-id')
        if not filter_form.cleaned_data['backsides'] and not order2 == 'transcriptions':
            photos = photos.filter(back_of__isnull=True)

        # FIXME: values aren't used
        # idea is to show page where the selected photo is
        # Warning: all photos is very slow
        #
        #        if requested_photo:
        #            ids = list(photos.values_list('id', flat=True))
        #            if requested_photo.id in ids:
        #                photo_count_before_requested = ids.index(requested_photo.id)
        #                page = ceil(float(photo_count_before_requested) / float(page_size))

        # Note seeking (start:end) has been here done when results are limited using photo_ids above
        if albumsize_before_sorting:
            start, end, total, max_page, page = get_pagination_parameters(page, page_size, albumsize_before_sorting)
            # limit QuerySet to selected photos so it is faster to evaluate in next steps
            photos_ids = list(photos.values_list('id', flat=True)[start:end])
            photos = photos.filter(id__in=photos_ids)
        else:
            photos_ids = list(photos.values_list('id', flat=True))
            start, end, total, max_page, page = get_pagination_parameters(page, page_size, len(photos_ids))
            # limit QuerySet to selected photos so it is faster to evaluate in next steps
            photos = photos.filter(id__in=photos_ids[start:end])

        # FIXME: Stupid
        if order1 == 'closest' and lat and lon:
            photos = photos.values_list('id', 'width', 'height', 'description', 'lat', 'lon', 'azimuth',
                                        'rephoto_count', 'comment_count', 'geotag_count', 'distance',
                                        'geotag_count', 'flip', 'has_similar', 'title', 'muis_title',
                                        'muis_comment', 'muis_event_description_set_note', 'geotag_count')
        else:
            photos = photos.values_list('id', 'width', 'height', 'description', 'lat', 'lon', 'azimuth',
                                        'rephoto_count', 'comment_count', 'geotag_count', 'geotag_count',
                                        'geotag_count', 'flip', 'has_similar', 'title', 'muis_title',
                                        'muis_comment', 'muis_event_description_set_note', 'geotag_count')

        photos = [list(i) for i in photos]
        if default_ordering and album and album.ordered:
            album_photos_links_order = AlbumPhoto.objects.filter(album=album).order_by('pk').values_list('photo_id',
                                                                                                         flat=True)
            for each in album_photos_links_order:
                photos = sorted(photos, key=lambda x: x[0] == each)
        # FIXME: Replacing objects with arrays is not a good idea, the small speed boost isn't worth it
        for p in photos:
            if p[3] is not None and p[3] != "" and p[14] is not None and p[14] != "":
                p[3] = p[14] + (". " if p[14][-1] != "." else " ") + p[
                    3]  # add title to image description if both are present.

            # Failback width/height for photos which imagedata is not saved yet
            if p[1] == '' or p[1] is None:
                p[1] = 400
            if p[2] == '' or p[2] is None:
                p[2] = 400
            if p[3] == '' or p[3] is None:
                p[3] = p[14]
            if p[3] == '' or p[3] is None:
                p[3] = p[15]
            if p[3] == '' or p[3] is None:
                p[3] = p[16]
            if p[3] == '' or p[3] is None:
                p[3] = p[17]
            if p[2] >= 1080:
                p[18] = True
            else:
                p[18] = False
            if hasattr(p[10], 'm'):
                p[10] = p[10].m
            p[1], p[2] = calculate_thumbnail_size(p[1], p[2], 400)
            if 'photo_selection' in request.session:
                p[11] = 1 if str(p[0]) in request.session['photo_selection'] else 0
            else:
                p[11] = 0
            p.append(get_pseudo_slug_for_photo(p[3], None, p[0]))
        if album:
            context['album'] = (
                album.id,
                album.name,
                ','.join(album.name.split(' ')),
                album.lat,
                album.lon,
                album.is_film_still_album,
                album.get_album_type
            )
            context['videos'] = VideoSerializer(album.videos.all(), many=True).data
        else:
            context['album'] = None
        fb_share_photos = []
        if requested_photo:
            context['photo'] = [
                requested_photo.pk,
                requested_photo.get_pseudo_slug(),
                requested_photo.width,
                requested_photo.height
            ]
            fb_share_photos = [context['photo']]
        else:
            context['photo'] = None
            fb_id_list = [p[0] for p in photos[:5]]
            qs_for_fb = Photo.objects.filter(id__in=fb_id_list)
            for p in qs_for_fb:
                fb_share_photos.append([p.id, p.get_pseudo_slug(), p.width, p.height])
        context['photos'] = photos
        context['show_photos'] = show_photos
        # FIXME: DRY
        context['fb_share_photos'] = fb_share_photos
        context['start'] = start
        context['end'] = end
        context['photos_with_comments'] = photos_with_comments
        context['photos_with_rephotos'] = photos_with_rephotos
        context['photos_with_similar_photos'] = photos_with_similar_photos
        context['page'] = page
        context['total'] = total
        context['max_page'] = max_page
        context['my_likes_only'] = my_likes_only
        context['rephotos_by'] = rephotos_by_id
        context['rephotos_by_name'] = rephotos_by_name
    else:
        context['album'] = None
        context['photo'] = None
        context['photos_with_comments'] = photos.filter(comment_count__isnull=False).count()
        context['photos_with_rephotos'] = photos.filter(rephoto_count__isnull=False).count()
        context['photos_with_similar_photos'] = photos.filter(similar_photos__isnull=False)
        photos = photos.values_list('id', 'width', 'height', 'description', 'lat', 'lon', 'azimuth',
                                    'rephoto_count', 'comment_count', 'geotag_count', 'geotag_count',
                                    'geotag_count', 'title', 'muis_title', 'muis_comment',
                                    'muis_event_description_set_note')[0:page_size]
        fb_share_photos = []
        fb_id_list = [p[0] for p in photos[:5]]
        qs_for_fb = Photo.objects.filter(id__in=fb_id_list)
        for p in qs_for_fb:
            fb_share_photos.append([p.id, p.get_pseudo_slug(), p.width, p.height])
        context['fb_share_photos'] = fb_share_photos
        context['order1'] = 'time'
        context['order2'] = 'added'
        context['order3'] = ''
        context['is_photoset'] = False
        context['my_likes_only'] = False
        context['rephotos_by'] = None
        context['rephotos_by_name'] = None
        context['total'] = photos.count()
        photos = [list(each) for each in photos]
        for p in photos:
            p[1], p[2] = calculate_thumbnail_size(p[1], p[2], 400)
            if 'photo_selection' in request.session:
                p[11] = 1 if str(p[0]) in request.session['photo_selection'] else 0
            else:
                p[11] = 0
        context['photos'] = photos
        context['start'] = 0
        context['end'] = page_size
        context['page'] = 1
        context['show_photos'] = False
        context['max_page'] = ceil(float(context['total']) / float(page_size))

    context['execution_time'] = str(time() - start_time)
    return context


def photo_selection(request):
    form = PhotoSelectionForm(request.POST)
    if 'photo_selection' not in request.session:
        request.session['photo_selection'] = {}
    if form.is_valid():
        if form.cleaned_data['clear']:
            request.session['photo_selection'] = {}
        elif form.cleaned_data['id']:
            photo_id = str(form.cleaned_data['id'].id)
            helper = request.session['photo_selection']
            if photo_id not in request.session['photo_selection']:
                helper[photo_id] = True
            else:
                del helper[photo_id]
            request.session['photo_selection'] = helper

    return HttpResponse(json.dumps(request.session['photo_selection']), content_type='application/json')


def list_photo_selection(request):
    photos = None
    at_least_one_photo_has_location = False
    count_with_location = 0
    whole_set_albums_selection_form = CuratorWholeSetAlbumsSelectionForm()
    if 'photo_selection' in request.session:
        photos = Photo.objects.filter(pk__in=request.session['photo_selection']).values_list('id', 'width', 'height',
                                                                                             'flip', 'description',
                                                                                             'lat', 'lon')
        photos = [list(each) for each in photos]
        for p in photos:
            if p[5] and p[6]:
                at_least_one_photo_has_location = True
                count_with_location += 1
            p[1], p[2] = calculate_thumbnail_size_max_height(p[1], p[2], 300)
    context = {
        'is_selection': True,
        'photos': photos,
        'at_least_one_photo_has_location': at_least_one_photo_has_location,
        'count_with_location': count_with_location,
        'whole_set_albums_selection_form': whole_set_albums_selection_form
    }

    return render(request, 'photo/selection/photo_selection.html', context)


def upload_photo_selection(request):
    form = SelectionUploadForm(request.POST)
    context = {
        'ajapaik_facebook_link': settings.AJAPAIK_FACEBOOK_LINK,
        'error': False
    }
    profile = request.get_user().profile
    if form.is_valid() and profile.is_legit():
        albums = Album.objects.filter(id__in=request.POST.getlist('albums'))
        photo_ids = json.loads(form.cleaned_data['selection'])

        if not albums.exists():
            context['error'] = _('Cannot upload to these albums')

        album_photos = []
        points = []
        for a in albums:
            for pid in photo_ids:
                try:
                    p = Photo.objects.get(pk=pid)
                    existing_link = AlbumPhoto.objects.filter(album=a, photo_id=pid).first()
                    if not existing_link:
                        album_photos.append(
                            AlbumPhoto(photo=p,
                                       album=a,
                                       profile=profile,
                                       type=AlbumPhoto.RECURATED
                                       )
                        )
                        points.append(
                            Points(user=profile, action=Points.PHOTO_RECURATION, photo_id=pid, points=30, album=a,
                                   created=timezone.now()))
                except:  # noqa
                    pass
                if a.cover_photo is None and p is not None:
                    a.cover_photo = p

        AlbumPhoto.objects.bulk_create(album_photos)
        Points.objects.bulk_create(points)

        for a in albums:
            a.set_calculated_fields()
            a.light_save()

        profile.set_calculated_fields()
        profile.save()
        context['message'] = _('Recuration successful')
    else:
        context['error'] = _('Faulty data submitted')

    return HttpResponse(json.dumps(context), content_type='application/json')


# FIXME: This should either be used more or not at all
def _make_fullscreen(p):
    if p and p.image:
        return {'url': p.image.url, 'size': [p.image.width, p.image.height]}


@ensure_csrf_cookie
def photo_slug(request, photo_id=None, pseudo_slug=None):
    # Because of some bad design decisions, we have a URL /photo, let's just give a last photo
    if photo_id is None:
        photo_id = Photo.objects.last().pk
    # TODO: Should replace slug with correct one, many thing to keep in mind though:
    #  Google indexing, Facebook shares, comments, likes etc.
    profile = request.get_user().profile
    photo_obj = get_object_or_404(Photo, id=photo_id)

    user_has_likes = profile.likes.exists()
    user_has_rephotos = profile.photos.filter(rephoto_of__isnull=False).exists()

    # switch places if rephoto url
    rephoto = None
    first_rephoto = None
    if hasattr(photo_obj, 'rephoto_of') and photo_obj.rephoto_of is not None:
        rephoto = photo_obj
        photo_obj = photo_obj.rephoto_of

    geotag_count = 0
    azimuth_count = 0
    original_thumb_size = None
    first_geotaggers = []
    if photo_obj:
        original_thumb_size = get_thumbnail(photo_obj.image, '1024x1024').size
        geotags = GeoTag.objects.filter(photo_id=photo_obj.id).distinct('user_id').order_by('user_id', '-created')
        geotag_count = geotags.count()
        if geotag_count > 0:
            correct_geotags_from_authenticated_users = geotags.exclude(user__pk=profile.user_id).filter(
                Q(user__first_name__isnull=False, user__last_name__isnull=False, is_correct=True))[:3]
            if correct_geotags_from_authenticated_users.exists():
                for each in correct_geotags_from_authenticated_users:
                    first_geotaggers.append([each.user.get_display_name, each.lat, each.lon, each.azimuth])
            first_geotaggers = json.dumps(first_geotaggers)
        azimuth_count = geotags.filter(azimuth__isnull=False).count()
        first_rephoto = photo_obj.rephotos.all().first()

    if request.get_user().username != settings.BOT_USERNAME:
        user_view_array = request.session.get('user_view_array', [])

        if photo_obj.id not in user_view_array:
            photo_obj.view_count += 1
            user_view_array.append(photo_obj.id)
            request.session['user_view_array'] = user_view_array

        now = timezone.now()
        if not photo_obj.first_view:
            photo_obj.first_view = now

        photo_obj.latest_view = now
        photo_obj.light_save()
        request.session.modified = True

    is_frontpage = False
    is_mapview = False
    is_selection = False
    if is_ajax(request):
        template = 'photo/_photo_modal.html'
        if request.GET.get('isFrontpage'):
            is_frontpage = True
        if request.GET.get('isMapview'):
            is_mapview = True
        if request.GET.get('isSelection'):
            is_selection = True
    else:
        template = 'photo/photoview.html'

    if not photo_obj.get_display_text:
        title = 'Unknown photo'
    else:
        title = ' '.join(photo_obj.get_display_text.split(' ')[:5])[:50]

    if photo_obj.author:
        title += f' – {photo_obj.author}'

    album_ids = AlbumPhoto.objects.filter(photo_id=photo_obj.id).values_list('album_id', flat=True)
    full_album_id_list = list(album_ids)
    albums = Album.objects.filter(pk__in=album_ids, atype=Album.CURATED).prefetch_related('subalbum_of')
    collection_albums = Album.objects.filter(pk__in=album_ids, atype=Album.COLLECTION)
    for each in albums:
        if each.subalbum_of:
            current_parent = each.subalbum_of
            while current_parent is not None:
                full_album_id_list.append(current_parent.id)
                current_parent = current_parent.subalbum_of
    albums = Album.objects.filter(pk__in=full_album_id_list, atype=Album.CURATED)
    for a in albums:
        first_albumphoto = AlbumPhoto.objects.filter(photo_id=photo_obj.id, album=a).first()
        if first_albumphoto:
            a.this_photo_curator = first_albumphoto.profile
    album = albums.first()
    next_photo = None
    previous_photo = None
    if album:
        album_selection_form = AlbumSelectionForm({'album': album.id})
        if not is_ajax(request):
            next_photo_id = \
                AlbumPhoto.objects.filter(photo_id__gt=photo_obj.pk, album=album.id).aggregate(min_id=Min('photo_id'))[
                    'min_id']
            if next_photo_id:
                # AlbumPhotos can return something which is filtered out by our custom manager, don't use .get() here.
                next_photo = Photo.objects.filter(pk=next_photo_id).first()

            previous_photo_id = \
                AlbumPhoto.objects.filter(photo_id__lt=photo_obj.pk, album=album.id).aggregate(max_id=Max('photo_id'))[
                    'max_id']
            if previous_photo_id:
                # AlbumPhotos can return something which is filtered out by our custom manager, don't use .get() here.
                previous_photo = Photo.objects.filter(pk=previous_photo_id).first()
    else:
        album_selection_form = AlbumSelectionForm(
            initial={'album': Album.objects.filter(is_public=True).order_by('-created').first()}
        )
        if not is_ajax(request):
            next_photo_id = Photo.objects.filter(pk__gt=photo_obj.pk).aggregate(min_id=Min('id'))['min_id']
            if next_photo_id:
                # AlbumPhotos can return something which is filtered out by our custom manager, don't use .get() here.
                next_photo = Photo.objects.filter(pk=next_photo_id).first()

            previous_photo_id = Photo.objects.filter(pk__lt=photo_obj.pk).aggregate(max_id=Max('id'))['max_id']
            if previous_photo_id:
                # AlbumPhotos can return something which is filtered out by our custom manager, don't use .get() here.
                previous_photo = Photo.objects.filter(pk=previous_photo_id).first()

    if album:
        album = (album.id, album.lat, album.lon)

    rephoto_fullscreen = None
    if first_rephoto is not None:
        rephoto_fullscreen = _make_fullscreen(first_rephoto)

    if photo_obj and photo_obj.get_display_text:
        photo_obj.tags = ','.join(photo_obj.get_display_text.split(' '))
    if rephoto and rephoto.get_display_text:
        rephoto.tags = ','.join(rephoto.get_display_text.split(' '))

    if 'photo_selection' in request.session:
        if str(photo_obj.id) in request.session['photo_selection']:
            photo_obj.in_selection = True

    user_confirmed_this_location = 'false'
    user_has_geotagged = GeoTag.objects.filter(photo=photo_obj, user=profile).exists()
    if user_has_geotagged:
        user_has_geotagged = 'true'
    else:
        user_has_geotagged = 'false'
    last_user_confirm_geotag_for_this_photo = GeoTag.objects.filter(type=GeoTag.CONFIRMATION, photo=photo_obj,
                                                                    user=profile) \
        .order_by('-created').first()
    if last_user_confirm_geotag_for_this_photo:
        if last_user_confirm_geotag_for_this_photo.lat == photo_obj.lat \
                and last_user_confirm_geotag_for_this_photo.lon == photo_obj.lon:
            user_confirmed_this_location = 'true'

    photo_obj.user_likes = False
    photo_obj.user_loves = False
    likes = PhotoLike.objects.filter(photo=photo_obj)
    photo_obj.like_count = likes.distinct('profile').count()
    like = likes.filter(profile=profile).first()
    if like:
        if like.level == 1:
            photo_obj.user_likes = True
        elif like.level == 2:
            photo_obj.user_loves = True

    previous_datings = photo_obj.datings.order_by('created').prefetch_related('confirmations')
    for each in previous_datings:
        each.this_user_has_confirmed = each.confirmations.filter(profile=profile).exists()
    serialized_datings = DatingSerializer(previous_datings, many=True).data
    serialized_datings = JSONRenderer().render(serialized_datings).decode('utf-8')

    strings = []
    if photo_obj.source:
        strings = [photo_obj.source.description, photo_obj.source_key]
    desc = ' '.join(filter(None, strings))

    next_similar_photo = photo_obj
    if next_photo is not None:
        next_similar_photo = next_photo
    compare_photos_url = request.build_absolute_uri(
        reverse('compare-photos', args=(photo_obj.id, next_similar_photo.id)))
    image_similarities = ImageSimilarity.objects.filter(from_photo_id=photo_obj.id).exclude(similarity_type=0)
    if image_similarities.exists():
        compare_photos_url = request.build_absolute_uri(
            reverse('compare-photos', args=(photo_obj.id, image_similarities.first().to_photo_id)))

    people = [x.name for x in photo_obj.people]
    similar_photos = ImageSimilarity.objects.filter(from_photo=photo_obj.id).exclude(similarity_type=0)

    similar_fullscreen = None
    if similar_photos.all().first() is not None:
        similar_fullscreen = _make_fullscreen(similar_photos.all().first().to_photo)

    whole_set_albums_selection_form = CuratorWholeSetAlbumsSelectionForm()

    reverse_side = None
    if photo_obj.back_of is not None:
        reverse_side = photo_obj.back_of
    elif photo_obj.front_of is not None:
        reverse_side = photo_obj.front_of

    seconds = None
    if photo_obj.video_timestamp:
        seconds = photo_obj.video_timestamp / 1000

    context = {
        'photo': photo_obj,
        'similar_photos': similar_photos,
        'previous_datings': serialized_datings,
        'datings_count': previous_datings.count(),
        'original_thumb_size': original_thumb_size,
        'user_confirmed_this_location': user_confirmed_this_location,
        'user_has_geotagged': user_has_geotagged,
        'fb_url': request.build_absolute_uri(reverse('photo', args=(photo_obj.id,))),
        'licence': Licence.objects.get(id=17),  # CC BY 4.0
        'area': photo_obj.area,
        'album': album,
        'albums': albums,
        'collection_albums': collection_albums,
        'is_frontpage': is_frontpage,
        'is_mapview': is_mapview,
        'is_selection': is_selection,
        'album_selection_form': album_selection_form,
        'geotag_count': geotag_count,
        'azimuth_count': azimuth_count,
        'fullscreen': _make_fullscreen(photo_obj),
        'rephoto_fullscreen': rephoto_fullscreen,
        'similar_fullscreen': similar_fullscreen,
        'title': title,
        'description': desc,
        'rephoto': rephoto,
        'hostname': request.build_absolute_uri('/'),
        'first_geotaggers': first_geotaggers,
        'is_photoview': True,
        'ajapaik_facebook_link': settings.AJAPAIK_FACEBOOK_LINK,
        'user_has_likes': user_has_likes,
        'user_has_rephotos': user_has_rephotos,
        'next_photo': next_photo,
        'previous_photo': previous_photo,
        'similar_photo_count': similar_photos.count(),
        'confirmed_similar_photo_count': similar_photos.filter(confirmed=True).count(),
        'compare_photos_url': compare_photos_url,
        'reverse_side': reverse_side,
        'is_photo_modal': is_ajax(request),
        # TODO: Needs more data than just the names
        'people': people,
        'whole_set_albums_selection_form': whole_set_albums_selection_form,
        'seconds': seconds
    }

    return render(request, template, context)


@ensure_csrf_cookie
def mapview(request, photo_id=None, rephoto_id=None):
    profile = request.get_user().profile
    area_selection_form = AreaSelectionForm(request.GET)
    game_album_selection_form = GameAlbumSelectionForm(request.GET)
    albums = _get_album_choices(None, 0, 1)  # Where albums variable is used?
    photos_qs = Photo.objects.filter(rephoto_of__isnull=True).values('id')
    select_all_photos = True

    user_has_likes = profile.likes.exists()
    user_has_rephotos = profile.photos.filter(rephoto_of__isnull=False).exists()

    area = None
    album = None
    if area_selection_form.is_valid():
        select_all_photos = False
        area = area_selection_form.cleaned_data['area']
        photos_qs = photos_qs.filter(area=area)

    if game_album_selection_form.is_valid():
        select_all_photos = False
        album = game_album_selection_form.cleaned_data['album']
        photos_qs = album.photos.prefetch_related('subalbums')
        for sa in album.subalbums.exclude(atype=Album.AUTO):
            photos_qs = photos_qs | sa.photos.filter(rephoto_of__isnull=True)

    selected_photo = None
    selected_rephoto = None
    if rephoto_id:
        selected_rephoto = Photo.objects.filter(pk=rephoto_id).first()

    if photo_id:
        selected_photo = Photo.objects.filter(pk=photo_id).first()
    else:
        if selected_rephoto:
            selected_photo = Photo.objects.filter(pk=selected_rephoto.rephoto_of.id).first()

    if selected_photo and album is None:
        photo_album_ids = AlbumPhoto.objects.filter(photo_id=selected_photo.id).values_list('album_id', flat=True)
        album = Album.objects.filter(pk__in=photo_album_ids, is_public=True).order_by('-created').first()
        if album:
            select_all_photos = False
            photos_qs = album.photos.prefetch_related('subalbums').filter(rephoto_of__isnull=True)
            for sa in album.subalbums.exclude(atype=Album.AUTO):
                photos_qs = photos_qs | sa.photos.filter(rephoto_of__isnull=True)

    if selected_photo and area is None:
        select_all_photos = False
        area = Area.objects.filter(pk=selected_photo.area_id).first()
        photos_qs = photos_qs.filter(area=area, rephoto_of__isnull=True)

    # If we using unfiltered view then we can just count all geotags

    if True:
        geotagging_user_count = 0
        total_photo_count = 0
    elif select_all_photos:
        geotagging_user_count = GeoTag.objects.distinct('user').values('user').count()
        total_photo_count = photos_qs.count()
    else:
        geotagging_user_count = GeoTag.objects.filter(photo_id__in=photos_qs.values_list('id', flat=True)).distinct(
            'user').values('user').count()
        total_photo_count = photos_qs.distinct('id').values('id').count()

    if True:
        geotagged_photo_count = 0
    else:
        geotagged_photo_count = photos_qs.distinct('id').filter(lat__isnull=False, lon__isnull=False).count()

    if geotagged_photo_count:
        last_geotagged_photo_id = Photo.objects.order_by(F('latest_geotag').desc(nulls_last=True)).values('id').first()[
            'id']
    else:
        last_geotagged_photo_id = None

    context = {'area': area, 'last_geotagged_photo_id': last_geotagged_photo_id,
               'total_photo_count': total_photo_count, 'geotagging_user_count': geotagging_user_count,
               'geotagged_photo_count': geotagged_photo_count, 'albums': albums,
               'hostname': request.build_absolute_uri('/'),
               'selected_photo': selected_photo, 'selected_rephoto': selected_rephoto, 'is_mapview': True,
               'ajapaik_facebook_link': settings.AJAPAIK_FACEBOOK_LINK, 'album': None, 'user_has_likes': user_has_likes,
               'user_has_rephotos': user_has_rephotos, 'query_string': request.GET.get('q')}

    if album is not None:
        context['album'] = (album.id, album.name, album.lat, album.lon, ','.join(album.name.split(' ')))
        context['title'] = f'{album.name} - {_("Browse photos on map")}'
        context['facebook_share_photos'] = []
        facebook_share_photos = album.photos.all()[:5]
        for each in facebook_share_photos:
            each = [each.pk, each.get_pseudo_slug(), each.width, each.height]
            context['facebook_share_photos'].append(each)
    elif area is not None:
        context['title'] = f'{area.name} - {_("Browse photos on map")}'
    else:
        context['title'] = _('Browse photos on map')
    context['show_photos'] = True
    return render(request, 'common/mapview.html', context)


def map_objects_by_bounding_box(request):
    form = MapDataRequestForm(request.POST)

    if form.is_valid():
        album = form.cleaned_data['album']
        area = form.cleaned_data['area']
        limit_by_album = form.cleaned_data['limit_by_album']
        sw_lat = form.cleaned_data['sw_lat']
        sw_lon = form.cleaned_data['sw_lon']
        ne_lat = form.cleaned_data['ne_lat']
        ne_lon = form.cleaned_data['ne_lon']
        count_limit = form.cleaned_data['count_limit']
        query_string = form.cleaned_data['query_string']

        qs = Photo.objects.filter(
            lat__isnull=False, lon__isnull=False, rephoto_of__isnull=True
        )

        if album and limit_by_album:
            album_photo_ids = album.get_historic_photos_queryset_with_subalbums().values_list('id', flat=True)
            qs = qs.filter(id__in=album_photo_ids)

        if area:
            qs = qs.filter(area=area)

        if sw_lat and sw_lon and ne_lat and ne_lon:
            qs = qs.filter(lat__gte=sw_lat, lon__gte=sw_lon, lat__lte=ne_lat, lon__lte=ne_lon)

        if query_string:
            qs = qs.filter(Q(description_et__icontains=query_string) | Q(description_fi__icontains=query_string) | Q(
                description_sv__icontains=query_string) | Q(description_nl__icontains=query_string) | Q(
                description_lv__icontains=query_string) | Q(description_lt__icontains=query_string) | Q(
                description_de__icontains=query_string) | Q(description_ru__icontains=query_string) | Q(
                author__icontains=query_string) | Q(types__icontains=query_string) | Q(
                keywords__icontains=query_string) | Q(source_key__icontains=query_string) | Q(
                source__name__icontains=query_string) | Q(address__icontains=query_string))

        if count_limit:
            qs = qs.order_by('?')[:count_limit]

        data = {
            'photos': PhotoMapMarkerSerializer(
                qs,
                many=True,
                photo_selection=request.session.get('photo_selection', [])
            ).data
        }
    else:
        data = {
            'photos': []
        }

    return JsonResponse(data)


def public_add_album(request):
    # FIXME: ModelForm
    add_album_form = AddAlbumForm(request.POST)
    if add_album_form.is_valid():
        user_profile = request.get_user().profile
        name = add_album_form.cleaned_data['name']
        description = add_album_form.cleaned_data['description']
        if user_profile:
            new_album = Album(
                name=name, description=description, atype=Album.COLLECTION, profile=user_profile, is_public=False)
            new_album.save()
            selectable_albums = Album.objects.filter(Q(atype=Album.FRONTPAGE) | Q(profile=user_profile))
            selectable_albums = [{'id': x.id, 'name': x.name} for x in selectable_albums]
            return HttpResponse(json.dumps(selectable_albums), content_type='application/json')
    return HttpResponse(json.dumps('Error'), content_type='application/json', status=400)


def public_add_area(request):
    add_area_form = AddAreaForm(request.POST)
    # TODO: Better duplicate handling
    if add_area_form.is_valid():
        try:
            Area.objects.get(name=add_area_form.cleaned_data['name'])
        except ObjectDoesNotExist:
            user_profile = request.get_user().profile
            name = add_area_form.cleaned_data['name']
            lat = add_area_form.cleaned_data['lat']
            lon = add_area_form.cleaned_data['lon']
            if user_profile:
                new_area = Area(name=name, lat=lat, lon=lon)
                new_area.save()
                selectable_areas = Area.objects.order_by('name').all()
                selectable_areas = [{'id': x.id, 'name': x.name} for x in selectable_areas]
                return HttpResponse(json.dumps(selectable_areas), content_type='application/json')
    return HttpResponse(json.dumps('Error'), content_type='application/json', status=400)


def update_like_state(request):
    profile = request.get_user().profile
    form = PhotoLikeForm(request.POST)
    context = {}
    if form.is_valid() and profile:
        p = form.cleaned_data['photo']
        like = PhotoLike.objects.filter(photo=p, profile=profile).first()
        if like:
            if like.level == 1:
                like.level = 2
                like.save()
                context['level'] = 2
            elif like.level == 2:
                like.delete()
                context['level'] = 0
                p.first_like = None
                p.latest_list = None
        else:
            like = PhotoLike(
                profile=profile,
                photo=p,
                level=1
            )
            like.save()
            context['level'] = 1
        like_sum = p.likes.aggregate(Sum('level'))['level__sum']
        if not like_sum:
            like_sum = 0
        like_count = p.likes.distinct('profile').count()
        context['likeCount'] = like_count
        p.like_count = like_sum
        if like_count > 0:
            first_like = p.likes.order_by('created').first()
            latest_like = p.likes.order_by('-created').first()
            if first_like:
                p.first_like = first_like.created
            if latest_like:
                p.latest_like = latest_like.created
        else:
            p.first_like = None
            p.latest_like = None
        p.light_save()

    return HttpResponse(json.dumps(context), content_type='application/json')


def muis_import(request):
    user = request.user
    user_can_import = not user.is_anonymous and \
                      user.profile.is_legit and user.groups.filter(name='csv_uploaders').exists()
    if request.method == 'GET':
        url = 'https://www.muis.ee/OAIService/OAIService?verb=ListSets'
        url_response = urllib.request.urlopen(url)
        parser = ET.XMLParser(encoding="utf-8")
        tree = ET.fromstring(url_response.read(), parser=parser)
        ns = {'d': 'http://www.openarchives.org/OAI/2.0/'}
        sets = tree.findall('d:ListSets/d:set', ns)
        for s in sets:
            name = s.find('d:setName', ns).text
            spec = s.find('d:setSpec', ns).text
            existing = MuisCollection.objects.filter(spec=spec).first()
            if existing is None:
                MuisCollection(name=name, spec=spec).save()
            elif existing.name != name:
                existing.name = name
                existing.save()
        collections = MuisCollection.objects.filter(blacklisted=False)
        return render(request, 'muis-import.html', {
            'user_can_import': user_can_import,
            'collections': collections
        })


def photo_upload_choice(request):
    user = request.user
    context = {
        'is_upload_choice': True,
        'ajapaik_facebook_link': settings.AJAPAIK_FACEBOOK_LINK,
        'user_can_import_from_csv': user.is_superuser and user.groups.filter(name='csv_uploaders').exists(),
        'user_can_import_from_muis': user.is_superuser and user.groups.filter(name='csv_uploaders').exists()
    }

    return render(request, 'photo/upload/photo_upload_choice.html', context)


def redirect_view(request, photo_id=-1, thumb_size=-1, pseudo_slug=""):
    path = request.path

    if path.find('/ajapaikaja/') == 0:
        request.path = request.path.replace('/ajapaikaja/', '/game/')
    elif path.find('/kaart/') == 0:
        request.path = request.path.replace('/kaart/', '/map/')
    elif path.find('/foto_thumb/') == 0:
        request.path = request.path.replace('/foto_thumb/', '/photo-thumb/')
    elif path.find('/foto_url/') == 0:
        request.path = request.path.replace('/foto_url/', '/photo-thumb/')
    elif path.find('/foto_large/') == 0:
        request.path = request.path.replace('/foto_large/', '/photo-full/')
    elif path.find('/photo-large/') == 0:
        request.path = request.path.replace('/photo-large/', '/photo-full/')
    elif path.find('/photo-url/') == 0:
        request.path = request.path.replace('/photo-url/', '/photo-thumb/')
    elif path.find('/foto/') == 0:
        request.path = request.path.replace('/foto/', "/photo/")
    else:
        request.path = "/"

    response = redirect(request.get_full_path(), permanent=True)
    return response
