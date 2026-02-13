import random
import re
import string
import time
from django.db.models import Sum, Q, Count, F
from ajapaik.utils import get_etag, calculate_thumbnail_size, convert_to_degrees, calculate_thumbnail_size_max_height, \
    distance_in_meters, angle_diff, last_modified, suggest_photo_edit
from ajapaik.ajapaik.utils import get_pagination_parameters

from ajapaik.ajapaik.serializers import CuratorAlbumSelectionAlbumSerializer, CuratorMyAlbumListAlbumSerializer, \
    CuratorAlbumInfoSerializer, FrontpageAlbumSerializer, DatingSerializer, \
    VideoSerializer, PhotoMapMarkerSerializer
import requests
from django.core.management import BaseCommand
from ajapaik.ajapaik.models import Photo, Album, _get_pseudo_slug_for_photo
from ajapaik.ajapaik.views import Photo, Album, Profile
from django.conf import settings
from django.db.models import Q

from django.contrib.gis.db.models.functions import Distance, GeometryDistance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from ajapaik.ajapaik import forms
import json
import time
from datetime import timedelta
import numpy

class Command(BaseCommand):
    help = 'Register user and run predefined requests against API'
    baseurl = 'http://localhost:8000'

    def _get_estimated_count(self, qs):
        postgres_engines = ("postgis", "postgresql", "django_postgrespool")
        engine = settings.DATABASES[qs.db]["ENGINE"].split(".")[-1]
        is_postgres = engine.startswith(postgres_engines)

        counter=0

        if is_postgres:
            print("Estimation")
            starttime = time.time()
            estimated_count=0
            explain=qs.only('pk').explain()
            m=re.match(".*? rows=(\d+)", explain)
            if m:
                estimated_count=int(m[1])
            else:
                print("NOT FOUND")
        if estimated_count<30000:
            print(str(counter) + ": " + str((time.time() - starttime))) 
            starttime = time.time()
            real_count=qs.count()
            counter=counter+1
            print(str(counter) + ": " + str((time.time() - starttime))) 
            print(str(estimated_count) + "\t" + str(real_count) + "\t" +str(estimated_count-real_count))
            return real_count
        return estimated_count


    def _get_filtered_data_for_frontpage_simple(self, album_id=None, page_override=None):

        starttime_begin = time.time()
        starttime2 = time.time()
        starttime = time.time()

#        album=Album.objects.get(pk=1)
        order1 = ''
        order2 = ''
#        order1 = 'closest'
        order1 = 'time'
        order2 = 'rephotos'
#        order2 = 'geotags'
#        order2 = 'added'
        order3 = ''
#        order3 = 'reverse'
        start=0
        end=50
        album_id=None
#        album_id=67731
#        album_id=21
        counter=1
        lat=""
        lon=""
        lat = 60.195324067240776
        lon = 24.9251980263452

        filter_form_cleaned_data={}
        filter_form_cleaned_data['album']=album_id
        filter_form_cleaned_data['photo']=None
        filter_form_cleaned_data['photos']=None
        filter_form_cleaned_data['order1']=order1
        filter_form_cleaned_data['order2']=order2
        filter_form_cleaned_data['order3']=order3
        filter_form_cleaned_data['people']=None
        filter_form_cleaned_data['backsides']=None
        filter_form_cleaned_data['interiors']=None
        filter_form_cleaned_data['exteriors']=None
        filter_form_cleaned_data['ground_viewpoint_elevation']=None
        filter_form_cleaned_data['raised_viewpoint_elevation']=None
        filter_form_cleaned_data['aerial_viewpoint_elevation']=None
        filter_form_cleaned_data['no_geotags']=None
        filter_form_cleaned_data['high_quality']=None
        filter_form_cleaned_data['portrait']=None
        filter_form_cleaned_data['square']=None
        filter_form_cleaned_data['landscape']=None
        filter_form_cleaned_data['panoramic']=None
        filter_form_cleaned_data['rephotosBy']=None
        filter_form_cleaned_data['q']=None
        filter_form_cleaned_data['backsides']=None
        filter_form_cleaned_data['myLikes']=None
        filter_form_cleaned_data['lat']=lat
        filter_form_cleaned_data['lon']=lon
        filter_form_cleaned_data['page']=1

        context={}
        profile=Profile.objects.get(pk=44387121)
        photos = Photo.objects.filter(rephoto_of__isnull=True)
        page_size = settings.FRONTPAGE_DEFAULT_PAGE_SIZE
        page = filter_form_cleaned_data['page']

        if album_id:
            album = Album.objects.get(pk=album_id)
        else:
            album = filter_form_cleaned_data['album']

        requested_photo = filter_form_cleaned_data['photo']
        requested_photos = filter_form_cleaned_data['photos']
        order1 = filter_form_cleaned_data['order1']
        order2 = filter_form_cleaned_data['order2']
        order3 = filter_form_cleaned_data['order3']

        default_ordering = False
        if not order1 and not order2:
            order1 = 'time'
            order2 = 'added'
            default_ordering = True
        context['order1'] = order1
        context['order2'] = order2
        context['order3'] = order3
        my_likes_only = filter_form_cleaned_data['myLikes']
        rephotos_by_name = None
        rephotos_by_id = None

        rephotos_by = None

        counter=counter+1
        print(str(counter) + " a0: " + str((time.time() - starttime2))) 
        starttime2 = time.time()

        show_photos = True
        lat = filter_form_cleaned_data['lat']
        lon = filter_form_cleaned_data['lon']
        

        counter=counter+1
        print(str(counter) + " a00: " + str((time.time() - starttime2))) 
        starttime2 = time.time()


        print(photos.only('pk').query)

#        print("album_photo_ids: " + str(len(album_photo_ids)))


        counter=counter+1
        print(str(counter) + " a1: " + str((time.time() - starttime2))) 
        starttime2 = time.time()

        counter=counter+1
        print(str(counter) + " a1b: " + str((time.time() - starttime2))) 
        starttime2 = time.time()


        context['is_photoset'] = False
        photos_with_comments = None
        photos_with_rephotos = None
        photos_with_similar_photos = None
        q = filter_form_cleaned_data['q']


        if order1 == 'time':
            if order2 == 'rephotos':
                if order3 == 'reverse':
                    photos = photos.order_by(F('first_rephoto').asc(nulls_last=True))
                else:
                    photos = photos.order_by(F('latest_rephoto').desc(nulls_last=True))

                print(photos.filter(first_rephoto__isnull=False).only('id').query)
                photos_with_rephotos = photos.filter(first_rephoto__isnull=False).count()
                counter=counter+1
                print(str(counter) + "a3c: " + str((time.time() - starttime))) 
                starttime = time.time()


        if not filter_form_cleaned_data['backsides'] and not order2 == 'transcriptions':
            photos = photos.filter(back_of__isnull=True)

        counter=counter+1
        print(str(counter) + "aa: " + str((time.time() - starttime))) 
        starttime = time.time()

        print(photos.only('id').query)
        print(photos.count())
        start, end, total, max_page, page = get_pagination_parameters(page, page_size, photos.count())

        counter=counter+1
        print(str(counter) + "ab: " + str((time.time() - starttime))) 
        starttime = time.time()

        # Testing: Album.id 38516 = Photos – blacklisti
        # Moved here to limit the max blacklist ids sise to page_size for speed
        # Note: Blacklist will leak if new photos are blacklisted ones

        photos_ids = list(photos.values_list('id', flat=True)[start:(end+page_size)])
        if not album or album.id != 38516:
            blacklist_exists = Album.objects.filter(id=38516).exists()
            if blacklist_exists:
                exclude_photos = Album.objects.get(id=38516).photos.filter(pk__in=photos_ids).all()
                photos = photos.exclude(pk__in=exclude_photos).all()

        counter=counter+1
        print(str(counter) + "ac: " + str((time.time() - starttime))) 
        starttime = time.time()

        # Flatten the selected photos to ids so GeometryDistance indexed sort doesn't break in SQL-level
        # when rephoto count is annotated. This works because it force limits the number of sorted rows

        counter=counter+1
        print(str(counter) + "ad: " + str((time.time() - starttime))) 
        starttime = time.time()

        # Flatten the selected photos to ids so annotating rephotocount is faster in SQL
        # Needs to be investigated WHY this is faster and could it just be replaced with index
        if order1 == 'time' and order2 == 'rephotos':
            photo_ids=photos[start:end].values_list('id', flat=True)
            photos=Photo.objects.filter(id__in=photo_ids).all()
            if order3 == 'reverse':
                photos = photos.order_by(F('first_rephoto').asc(nulls_last=True))
            else:
                photos = photos.order_by(F('latest_rephoto').desc(nulls_last=True))

        counter=counter+1
        print(str(counter) + "ae: " + str((time.time() - starttime))) 
        starttime = time.time()

        photos = photos.values_list('id', 'width', 'height', 'description', 'lat', 'lon', 'azimuth',
                                        'rephoto_count', 'comment_count', 'geotag_count', 'geotag_count',
                                        'geotag_count', 'flip', 'has_similar', 'title', 'muis_title',
                                        'muis_comment', 'muis_event_description_set_note', 'geotag_count')[start:end]

        counter=counter+1
        print(str(counter) + "af: " + str((time.time() - starttime))) 
        starttime = time.time()

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

            # Failback width/height for photos which imagedata arent saved yet
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
            if 0 and 'photo_selection' in request.session:
                p[11] = 1 if str(p[0]) in request.session['photo_selection'] else 0
            else:
                p[11] = 0
            p.append(_get_pseudo_slug_for_photo(p[3], None, p[0]))
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
        context['execution_time'] = str(time.time() - starttime_begin)
        print( context['execution_time'])

    def _get_filtered_data_for_frontpage2(self, album_id=None, page_override=None):
        starttime_begin = time.time()
        starttime2 = time.time()
        starttime = time.time()

#        album=Album.objects.get(pk=1)
        order1 = ''
        order2 = ''
#        order1 = 'closest'
        order1 = 'time'
        order2 = 'rephotos'
#        order2 = 'geotags'
#        order2 = 'added'
        order3 = ''
#        order3 = 'reverse'
        start=0
        end=50
        album_id=None
#        album_id=67731
#        album_id=21
        counter=1
        lat=""
        lon=""
        lat = 60.195324067240776
        lon = 24.9251980263452

        filter_form_cleaned_data={}
        filter_form_cleaned_data['album']=album_id
        filter_form_cleaned_data['photo']=None
        filter_form_cleaned_data['photos']=None
        filter_form_cleaned_data['order1']=order1
        filter_form_cleaned_data['order2']=order2
        filter_form_cleaned_data['order3']=order3
        filter_form_cleaned_data['people']=None
        filter_form_cleaned_data['backsides']=None
        filter_form_cleaned_data['interiors']=None
        filter_form_cleaned_data['exteriors']=None
        filter_form_cleaned_data['ground_viewpoint_elevation']=None
        filter_form_cleaned_data['raised_viewpoint_elevation']=None
        filter_form_cleaned_data['aerial_viewpoint_elevation']=None
        filter_form_cleaned_data['no_geotags']=None
        filter_form_cleaned_data['high_quality']=None
        filter_form_cleaned_data['portrait']=None
        filter_form_cleaned_data['square']=None
        filter_form_cleaned_data['landscape']=None
        filter_form_cleaned_data['panoramic']=None
        filter_form_cleaned_data['rephotosBy']=None
        filter_form_cleaned_data['q']=None
        filter_form_cleaned_data['backsides']=None
        filter_form_cleaned_data['myLikes']=None
        filter_form_cleaned_data['lat']=lat
        filter_form_cleaned_data['lon']=lon
        filter_form_cleaned_data['page']=1

        context={}
        profile=Profile.objects.get(pk=44387121)
        photos = Photo.objects.filter(rephoto_of__isnull=True)
        page_size = settings.FRONTPAGE_DEFAULT_PAGE_SIZE

        if album_id:
            album = Album.objects.get(pk=album_id)
        else:
            album = filter_form_cleaned_data['album']

        requested_photo = filter_form_cleaned_data['photo']
        requested_photos = filter_form_cleaned_data['photos']
        order1 = filter_form_cleaned_data['order1']
        order2 = filter_form_cleaned_data['order2']
        order3 = filter_form_cleaned_data['order3']
        default_ordering = False
        if not order1 and not order2:
            order1 = 'time'
            order2 = 'added'
            default_ordering = True
        context['order1'] = order1
        context['order2'] = order2
        context['order3'] = order3
        my_likes_only = filter_form_cleaned_data['myLikes']
        rephotos_by_name = None
        rephotos_by_id = None
        if filter_form_cleaned_data['rephotosBy']:
            rephotos_by_name = filter_form_cleaned_data['rephotosBy'].get_display_name
            rephotos_by_id = filter_form_cleaned_data['rephotosBy'].pk
            rephotos_by = filter_form_cleaned_data['rephotosBy']
        else:
            rephotos_by = None

        counter=counter+1
        print(str(counter) + " a0: " + str((time.time() - starttime2))) 
        starttime2 = time.time()

        if not album and not requested_photos and not my_likes_only and not rephotos_by \
                and not filter_form_cleaned_data['order1']:
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
            context['execution_time'] = str(time.time() - starttime)
            return context
        else:
            show_photos = True
        lat = filter_form_cleaned_data['lat']
        lon = filter_form_cleaned_data['lon']
        if page_override:
            page = int(page_override)
        else:
            page = filter_form_cleaned_data['page']

        counter=counter+1
        print(str(counter) + " a00: " + str((time.time() - starttime2))) 
        starttime2 = time.time()


        print(photos.only('pk').query)

#        print("album_photo_ids: " + str(len(album_photo_ids)))


        counter=counter+1
        print(str(counter) + " a1: " + str((time.time() - starttime2))) 
        starttime2 = time.time()

        counter=counter+1
        print(str(counter) + " a1b: " + str((time.time() - starttime2))) 
        starttime2 = time.time()


        if filter_form_cleaned_data['people']:
            photos = photos.filter(face_recognition_rectangles__isnull=False,
                                   face_recognition_rectangles__deleted__isnull=True)
        if filter_form_cleaned_data['backsides']:
            photos = photos.filter(front_of__isnull=False)
        if filter_form_cleaned_data['interiors']:
            photos = photos.filter(scene=0)
        if filter_form_cleaned_data['exteriors']:
            photos = photos.exclude(scene=0)
        if filter_form_cleaned_data['ground_viewpoint_elevation']:
            photos = photos.exclude(viewpoint_elevation=1).exclude(viewpoint_elevation=2)
        if filter_form_cleaned_data['raised_viewpoint_elevation']:
            photos = photos.filter(viewpoint_elevation=1)
        if filter_form_cleaned_data['aerial_viewpoint_elevation']:
            photos = photos.filter(viewpoint_elevation=2)
        if filter_form_cleaned_data['no_geotags']:
            photos = photos.filter(geotag_count=0)
        if filter_form_cleaned_data['high_quality']:
            photos = photos.filter(height__gte=1080)
        if filter_form_cleaned_data['portrait']:
            photos = photos.filter(aspect_ratio__lt=0.95)
        if filter_form_cleaned_data['square']:
            photos = photos.filter(aspect_ratio__gte=0.95, aspect_ratio__lt=1.05)
        if filter_form_cleaned_data['landscape']:
            photos = photos.filter(aspect_ratio__gte=1.05, aspect_ratio__lt=2.0)
        if filter_form_cleaned_data['panoramic']:
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
        photos_with_comments = None
        photos_with_rephotos = None
        photos_with_similar_photos = None
        q = filter_form_cleaned_data['q']


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
        if not filter_form_cleaned_data['backsides'] and not order2 == 'transcriptions':
            photos = photos.filter(back_of__isnull=True)
        if requested_photo:
            ids = list(photos.values_list('id', flat=True))
            if requested_photo.id in ids:
                photo_count_before_requested = ids.index(requested_photo.id)
                page = ceil(float(photo_count_before_requested) / float(page_size))


        counter=counter+1
        print(str(counter) + "aa: " + str((time.time() - starttime))) 
        starttime = time.time()


        start, end, total, max_page, page = get_pagination_parameters(page, page_size, photos.count())

        counter=counter+1
        print(str(counter) + "ab: " + str((time.time() - starttime))) 
        starttime = time.time()

        # Testing: Album.id 38516 = Photos – blacklisti
        # Moved here to limit the max blacklist ids sise to page_size for speed
        # Note: Blacklist will leak if new photos are blacklisted ones

        photos_ids = list(photos.values_list('id', flat=True)[start:(end+page_size)])
        if not album or album.id != 38516:
            blacklist_exists = Album.objects.filter(id=38516).exists()
            if blacklist_exists:
                exclude_photos = Album.objects.get(id=38516).photos.filter(pk__in=photos_ids).all()
                photos = photos.exclude(pk__in=exclude_photos).all()

        counter=counter+1
        print(str(counter) + "ac: " + str((time.time() - starttime))) 
        starttime = time.time()

        # Flatten the selected photos to ids so GeometryDistance indexed sort doesn't break in SQL-level
        # when rephoto count is annotated. This works because it force limits the number of sorted rows
        if order1 == 'closest' and lat and lon:
            photo_ids=photos[start:end].values_list('id', flat=True)
            photos=Photo.objects.filter(id__in=photo_ids).all()
            if order3 == 'reverse':
                photos = photos.annotate(distance=GeometryDistance(('geography'), ref_location)).order_by('-distance')
            else:
                photos = photos.annotate(distance=GeometryDistance(('geography'), ref_location)).order_by('distance')

        counter=counter+1
        print(str(counter) + "ad: " + str((time.time() - starttime))) 
        starttime = time.time()

        # Flatten the selected photos to ids so annotating rephotocount is faster in SQL
        # Needs to be investigated WHY this is faster and could it just be replaced with index
        if order1 == 'time' and order2 == 'rephotos':
            photo_ids=photos[start:end].values_list('id', flat=True)
            photos=Photo.objects.filter(id__in=photo_ids).all()
            if order3 == 'reverse':
                photos = photos.order_by(F('first_rephoto').asc(nulls_last=True))
            else:
                photos = photos.order_by(F('latest_rephoto').desc(nulls_last=True))

        counter=counter+1
        print(str(counter) + "ae: " + str((time.time() - starttime))) 
        starttime = time.time()

        # FIXME: Stupid
        if order1 == 'closest' and lat and lon:
            # Note seeking (start:end) has been alredy done when values are flatted above
            photos = photos.values_list('id', 'width', 'height', 'description', 'lat', 'lon', 'azimuth',
                                        'rephoto_count', 'comment_count', 'geotag_count', 'distance',
                                        'geotag_count', 'flip', 'has_similar', 'title', 'muis_title',
                                        'muis_comment', 'muis_event_description_set_note', 'geotag_count')
        else:
            photos = photos.values_list('id', 'width', 'height', 'description', 'lat', 'lon', 'azimuth',
                                        'rephoto_count', 'comment_count', 'geotag_count', 'geotag_count',
                                        'geotag_count', 'flip', 'has_similar', 'title', 'muis_title',
                                        'muis_comment', 'muis_event_description_set_note', 'geotag_count')[start:end]

        counter=counter+1
        print(str(counter) + "af: " + str((time.time() - starttime))) 
        starttime = time.time()

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

            # Failback width/height for photos which imagedata arent saved yet
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
            if 0 and 'photo_selection' in request.session:
                p[11] = 1 if str(p[0]) in request.session['photo_selection'] else 0
            else:
                p[11] = 0
            p.append(_get_pseudo_slug_for_photo(p[3], None, p[0]))
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
        context['execution_time'] = str(time.time() - starttime_begin)
        print( context['execution_time'])


    def handle(self, *args, **options):
        self._get_filtered_data_for_frontpage_simple()


