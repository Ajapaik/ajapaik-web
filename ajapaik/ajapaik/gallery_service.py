from math import ceil
from time import time
from typing import Union

from django.conf import settings
from django.contrib.gis.db.models.functions import GeometryDistance
from django.contrib.gis.geos import Point
from django.db.models import Count, F
from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet

from ajapaik.ajapaik.models import Photo, Album, AlbumPhoto
from ajapaik.ajapaik.types import GalleryResults, UserMini, PaginationParameters
from ajapaik.ajapaik.utils import get_pagination_parameters


def _is_default_ordering(order1: str, order2: str, order3: Union[str, None]) -> bool:
    if order1 == 'time' and order2 == 'added' and not order3:
        return True
    else:
        return False


def get_filtered_data_for_gallery(
        profile,
        cleaned_data: dict,
        photo_filters: dict = {},
        page_size=None
) -> GalleryResults:
    start_time = time()
    # Why do we need to prefetch likes here?
    photos = Photo.objects.filter(rephoto_of__isnull=True, **photo_filters).prefetch_related("likes")
    page_size = page_size or settings.FRONTPAGE_DEFAULT_PAGE_SIZE

    album = cleaned_data['album']
    requested_photo = cleaned_data.get('photo')
    order1 = cleaned_data['order1'] or "time"
    order2 = cleaned_data['order2'] or "added"
    order3 = cleaned_data['order3']
    default_ordering = _is_default_ordering(order1, order2, order3)
    lat = cleaned_data.get('lat')
    lon = cleaned_data.get('lon')
    my_likes_only = cleaned_data.get('myLikes')
    date_from = cleaned_data["date_from"]
    date_to = cleaned_data["date_to"]
    page = cleaned_data.get('page')
    q = cleaned_data['q']

    if rephotos_by := cleaned_data.get('rephotosBy'):
        rephoto_album_author = UserMini(id=rephotos_by.id, name=rephotos_by.get_display_name) if rephotos_by else None
    else:
        rephoto_album_author = None

    # Do not show hidden photos
    if not album or album.id != 38516:
        blacklist_exists = Album.objects.filter(id=38516).exists()
        if blacklist_exists:
            photos = photos.exclude(albums__in=[38516])

    # FILTERING BELOW THIS LINE

    if album:
        sa_ids = [album.id, *album.subalbums.exclude(atype=Album.AUTO).values_list('id', flat=True)]
        photos = photos.filter(albums__in=sa_ids)

        # In QuerySet "albums__in" is 1:M JOIN so images will show up
        # multiple times in results so this needs to be distinct(). Distinct is slow.
        photos = photos.distinct()

    if cleaned_data['people']:
        photos = photos.filter(face_recognition_rectangles__isnull=False,
                               face_recognition_rectangles__deleted=None)

    if cleaned_data['backsides']:
        photos = photos.exclude(front_of=None)

    if cleaned_data['interiors']:
        photos = photos.filter(scene=0)
    elif cleaned_data['exteriors']:
        photos = photos.exclude(scene=0)

    if cleaned_data['ground_viewpoint_elevation']:
        photos = photos.exclude(viewpoint_elevation__in=[1, 2])
    elif cleaned_data['raised_viewpoint_elevation']:
        photos = photos.filter(viewpoint_elevation=1)
    elif cleaned_data['aerial_viewpoint_elevation']:
        photos = photos.filter(viewpoint_elevation=2)

    if cleaned_data['no_geotags']:
        photos = photos.filter(geotag_count=0)
    if cleaned_data['high_quality']:
        photos = photos.filter(height__gte=1080)

    if cleaned_data['portrait']:
        photos = photos.filter(aspect_ratio__lt=0.95)
    elif cleaned_data['square']:
        photos = photos.filter(aspect_ratio__gte=0.95, aspect_ratio__lt=1.05)
    elif cleaned_data['landscape']:
        photos = photos.filter(aspect_ratio__gte=1.05, aspect_ratio__lt=2.0)
    elif cleaned_data['panoramic']:
        photos = photos.filter(aspect_ratio__gte=2.0)

    if my_likes_only:
        photos = photos.filter(likes__profile=profile)

    if rephoto_album_author:
        photos = photos.filter(rephotos__user_id=rephoto_album_author.id)

    if date_from:
        photos = photos.filter(datings__start__gte=date_from)

    if date_to:
        photos = photos.filter(datings__end__lte=date_to)

    if q:
        sqs_ids = SearchQuerySet().models(Photo).filter(content=AutoQuery(q)).values_list("pk", flat=True)
        photos = photos.filter(pk__in=sqs_ids, rephoto_of__isnull=True)

    # In some cases it is faster to get the number of photos before we annotate new columns to it
    album_size_before_sorting = None
    if not album:
        album_size_before_sorting = Photo.objects.filter(pk__in=photos).cached_count(str(cleaned_data))

    photos_with_comments = None
    photos_with_rephotos = None

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
    if not cleaned_data['backsides'] and not order2 == 'transcriptions':
        photos = photos.filter(back_of__isnull=True)

    photo_ids = list(photos.values_list('id', flat=True))

    if requested_photo and requested_photo.id in photo_ids:
        photo_count_before_requested = photo_ids.index(requested_photo.id)
        page = ceil(float(photo_count_before_requested) / float(page_size))

    if page:
        # Note seeking (start:end) has been done when results are limited using photo_ids above
        total = album_size_before_sorting or len(photo_ids)
        start, end, max_page, page = get_pagination_parameters(page, total, page_size)
        pagination_parameters = PaginationParameters(
            start=start,
            end=end,
            page=page,
            total=total,
            max_page=max_page,
        )

        # limit QuerySet to selected photos, so it is faster to evaluate in next steps
        photos = photos.filter(id__in=photo_ids[start:end])
    else:
        pagination_parameters = None

    if default_ordering and album and album.ordered:
        album_photos_links_order = AlbumPhoto.objects.filter(album=album).order_by('pk').values_list('photo_id',
                                                                                                     flat=True)
        for each in album_photos_links_order:
            photos = sorted(photos, key=lambda x: x[0] == each)

    if requested_photo:
        fb_share_photos = [requested_photo]
    else:
        fb_share_photos = photos[:5]

    return GalleryResults(
        rephoto_album_author=rephoto_album_author,
        execution_time=str(time() - start_time),
        album=album,
        videos=[],
        photo=requested_photo,
        fb_share_photos=fb_share_photos,
        photos=photos.prefetch_related("source"),
        photos_with_comments=photos_with_comments,
        photos_with_rephotos=photos_with_rephotos,
        my_likes_only=my_likes_only,
        start=pagination_parameters.start if pagination_parameters else None,
        end=pagination_parameters.end if pagination_parameters else None,
        page=pagination_parameters.page if pagination_parameters else None,
        total=pagination_parameters.total if pagination_parameters else None,
        max_page=pagination_parameters.max_page if pagination_parameters else None,
        order1=order1,
        order2=order2,
        order3=order3,
    )
