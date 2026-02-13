from random import randint
from django.contrib.gis.geos import Point
import time
import json
from django.utils import timezone

import os
import re
from django.shortcuts import redirect, get_object_or_404, render
from django.db.models import Sum, Q, Count, F, Min, Max
from rest_framework.renderers import JSONRenderer

from ajapaik.ajapaik.serializers import AlbumSerializer, DatingSerializer
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import F, Sum, Q
from ajapaik.ajapaik.models import Photo, Album, Points, ImageSimilarity, Profile, GeoTag, Profile, AlbumPhoto, PhotoLike, Licence
from django.db import connection
from ajapaik.ajapaik.views import _get_album_choices, calculate_thumbnail_size
from ajapaik.ajapaik.forms import AddAlbumForm, AreaSelectionForm, AlbumSelectionForm, AddAreaForm,CuratorWholeSetAlbumsSelectionForm
from sorl.thumbnail import get_thumbnail
from django.conf import settings
from ajapaik.ajapaik.models import Photo
import time
from django.test.client import RequestFactory


def _make_fullscreen(p):
    if p and p.image:
        return {'url': p.image.url, 'size': [p.image.width, p.image.height]}

def test_photoslug(request=None, photo_id=None, profile=None):
    starttime2=time.time()

    starttime=time.time()
    # Because of some bad design decisions, we have a URL /photo, let's just give a random photo
    if photo_id is None:
#        photo_id = Photo.objects[:100].order_by('?').first().pk
        photo_id = Photo.objects.last().pk
    # TODO: Should replace slug with correct one, many thing to keep in mind though:
    #  Google indexing, Facebook shares, comments, likes etc.
##    profile = request.get_user().profile
    photo_obj = get_object_or_404(Photo, id=photo_id)

    print("A" + ": " + str(time.time() - starttime))
    starttime=time.time()

    user_has_likes = profile.likes.exists()
    user_has_rephotos = profile.photos.filter(rephoto_of__isnull=False).exists()

    # switch places if rephoto url
    rephoto = None
    first_rephoto = None
    if hasattr(photo_obj, 'rephoto_of') and photo_obj.rephoto_of is not None:
        rephoto = photo_obj
        photo_obj = photo_obj.rephoto_of

    print("B" + ": " + str(time.time() - starttime))
    starttime=time.time()

    geotag_count = 0   
    azimuth_count = 0
    original_thumb_size = None
    first_geotaggers = []
    if photo_obj:
        print("C" + ": " + str(time.time() - starttime))
        starttime=time.time()

        original_thumb_size = get_thumbnail(photo_obj.image, '1024x1024').size
        geotags = GeoTag.objects.filter(photo_id=photo_obj.id).distinct('user_id').order_by('user_id', '-created')
        geotag_count = geotags.count()
        print("C0" + ": " + str(time.time() - starttime))
        starttime=time.time()

        if geotag_count > 0:
            correct_geotags_from_authenticated_users = geotags.exclude(user__pk=profile.user_id).filter(
                Q(user__first_name__isnull=False, user__last_name__isnull=False, is_correct=True))[:3]
            if correct_geotags_from_authenticated_users.exists():
                for each in correct_geotags_from_authenticated_users:
                    first_geotaggers.append([each.user.get_display_name, each.lat, each.lon, each.azimuth])
            first_geotaggers = json.dumps(first_geotaggers)
        print("C1" + ": " + str(time.time() - starttime))
        starttime=time.time()

        azimuth_count = geotags.filter(azimuth__isnull=False).count()
        first_rephoto = photo_obj.rephotos.all().first()
#        if 'user_view_array' not in request.session:
#            request.session['user_view_array'] = []
#        if photo_obj.id not in request.session['user_view_array']:
        print("C2" + ": " + str(time.time() - starttime))
        starttime=time.time()

        photo_obj.view_count += 1
        now = timezone.now()
        if not photo_obj.first_view:
            photo_obj.first_view = now
        print("C3" + ": " + str(time.time() - starttime))
        starttime=time.time()

        photo_obj.latest_view = now
        photo_obj.light_save()
        print("C4" + ": " + str(time.time() - starttime))
        starttime=time.time()

#        request.session['user_view_array'].append(photo_obj.id)
#        request.session.modified = True

    print("D" + ": " + str(time.time() - starttime))
    starttime=time.time()

    is_frontpage = False
    is_mapview = False
    is_selection = False
#    if request.is_ajax():
#        template = 'photo/_photo_modal.html'
#        if request.GET.get('isFrontpage'):
#            is_frontpage = True
#        if request.GET.get('isMapview'):
#            is_mapview = True
#        if request.GET.get('isSelection'):
#            is_selection = True
#    else:
    template = 'photo/photoview.html'

    if not photo_obj.get_display_text:
        title = 'Unknown photo'
    else:
        title = ' '.join(photo_obj.get_display_text.split(' ')[:5])[:50]

    if photo_obj.author:
        title += f' – {photo_obj.author}'

    print("F" + ": " + str(time.time() - starttime))
    starttime=time.time()

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

    print("G" + ": " + str(time.time() - starttime))
    starttime=time.time()

    albums = Album.objects.filter(pk__in=full_album_id_list, atype=Album.CURATED)
    for a in albums:
        first_albumphoto = AlbumPhoto.objects.filter(photo_id=photo_obj.id, album=a).first()
        if first_albumphoto:
            a.this_photo_curator = first_albumphoto.profile

    print("H" + ": " + str(time.time() - starttime))
    starttime=time.time()

    album = albums.first()
    next_photo = None
    previous_photo = None

    if not album:
        print("H1" + ": " + str(time.time() - starttime))
        starttime=time.time()

        album_selection_form = AlbumSelectionForm({'album': album.id})
        if not False:
            print("H1A" + ": " + str(time.time() - starttime))
            starttime=time.time()

            next_photo_id = AlbumPhoto.objects.filter(photo__gt=photo_obj.pk,album=album.id).values('photo_id').aggregate(min_id=Min('photo_id'))['min_id']

            print("H1A4 " + str(next_photo_id) + ": " + str(time.time() - starttime))
            starttime=time.time()
            next_photo_id = AlbumPhoto.objects.filter(photo__gt=photo_obj.pk,album=album.id).order_by('photo_id').values('photo_id').first()['photo_id']  #aggregate(min_id=Min('id'))['min_id']
            print("H1A3 " + str(next_photo_id) + ": " + str(time.time() - starttime))
            starttime=time.time()

            print(album)
#            print(str(album.photos.filter(pk__gt=photo_obj.pk).aggregate(min_id=Min('id')).query))
            next_photo_id = album.photos.filter(pk__gt=photo_obj.pk).aggregate(min_id=Min('id'))['min_id']
            print("H1A1 " + str(next_photo_id) +  ": " + str(time.time() - starttime))
            starttime=time.time()

#            print(str(album.photos.filter(pk__gt=photo_obj.pk).order_by('pk').values('pk').query))
            next_photo_id = album.photos.filter(pk__gt=photo_obj.pk).order_by('pk').values('pk').first()['pk']  #aggregate(min_id=Min('id'))['min_id']
            print("H1A2 " + str(next_photo_id) + ": " + str(time.time() - starttime))
            starttime=time.time()


            if next_photo_id:
                next_photo = Photo.objects.get(pk=next_photo_id)  

            print("H1B0" + ": " + str(time.time() - starttime))
            starttime=time.time()

            previous_photo_id = album.photos.filter(pk__lt=photo_obj.pk).aggregate(max_id=Max('id'))['max_id']
            print("H1B1" + ": "  + str(previous_photo_id) + " "+ str(time.time() - starttime))
            starttime=time.time()


            previous_photo_id = AlbumPhoto.objects.filter(photo__lt=photo_obj.pk,album=album.id).values('photo_id').aggregate(max_id=Max('photo_id'))['max_id']
            print("H1B2" + ": "  + str(previous_photo_id) + " "+ str(time.time() - starttime))
            starttime=time.time()

            if previous_photo_id:
                previous_photo = Photo.objects.get(pk=previous_photo_id)
            print("H1C" + ": " + str(time.time() - starttime))
            starttime=time.time()

    else:
        print("H2" + ": " + str(time.time() - starttime))
        starttime=time.time()

        album_selection_form = AlbumSelectionForm(
            initial={'album': Album.objects.filter(is_public=True).order_by('-created').first()}
        )
        if not False:
            print("H4" + ": " + str(time.time() - starttime))
            starttime=time.time()

            next_photo_id = Photo.objects.filter(pk__gt=photo_obj.pk).aggregate(min_id=Min('id'))['min_id']
            if next_photo_id:
                next_photo = Photo.objects.get(pk=next_photo_id)

            print("H4A" + ": " + str(time.time() - starttime))
            starttime=time.time()

            previous_photo_id = Photo.objects.filter(pk__lt=photo_obj.pk).aggregate(max_id=Max('id'))['max_id']
            if previous_photo_id:
                previous_photo = Photo.objects.get(pk=previous_photo_id)

            print("H4B" + ": " + str(time.time() - starttime))
            starttime=time.time()

    print("I" + ": " + str(time.time() - starttime))
    starttime=time.time()

    if album:
        album = (album.id, album.lat, album.lon)

    rephoto_fullscreen = None
    if first_rephoto is not None:
        rephoto_fullscreen = _make_fullscreen(first_rephoto)

    print("I0" + ": " + str(time.time() - starttime))
    starttime=time.time()

    if photo_obj and photo_obj.get_display_text:
        photo_obj.tags = ','.join(photo_obj.get_display_text.split(' '))
    if rephoto and rephoto.get_display_text:
        rephoto.tags = ','.join(rephoto.get_display_text.split(' '))

#    if 'photo_selection' in request.session:
#        if str(photo_obj.id) in request.session['photo_selection']:
#            photo_obj.in_selection = True

    print("J" + ": " + str(time.time() - starttime))
    starttime=time.time()

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

    print("H" + ": " + str(time.time() - starttime))
    starttime=time.time()


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

    print("K" + ": " + str(time.time() - starttime))
    starttime=time.time()

    previous_datings = photo_obj.datings.order_by('created').prefetch_related('confirmations')
    for each in previous_datings:
        each.this_user_has_confirmed = each.confirmations.filter(profile=profile).exists()
    serialized_datings = DatingSerializer(previous_datings, many=True).data
    serialized_datings = JSONRenderer().render(serialized_datings).decode('utf-8')

    strings = []
    if photo_obj.source:
        strings = [photo_obj.source.description, photo_obj.source_key]
    desc = ' '.join(filter(None, strings))

    print("L" + ": " + str(time.time() - starttime))
    starttime=time.time()


    next_similar_photo = photo_obj
    if next_photo is not None:
        next_similar_photo = next_photo
    compare_photos_url = "https://yahoo.com" #request.build_absolute_uri(
#        reverse('compare-photos', args=(photo_obj.id, next_similar_photo.id)))
    imageSimilarities = ImageSimilarity.objects.filter(from_photo_id=photo_obj.id).exclude(similarity_type=0)
    if imageSimilarities.exists():
        compare_photos_url = "https://google.com" #request.build_absolute_uri(
#            reverse('compare-photos', args=(photo_obj.id, imageSimilarities.first().to_photo_id)))

    print("M" + ": " + str(time.time() - starttime))
    starttime=time.time()

    people = [x.name for x in photo_obj.people] 
    similar_photos = ImageSimilarity.objects.filter(from_photo=photo_obj.id).exclude(similarity_type=0)

    similar_fullscreen = None
    if similar_photos.all().first() is not None:
        similar_fullscreen = _make_fullscreen(similar_photos.all().first().to_photo)

    whole_set_albums_selection_form = CuratorWholeSetAlbumsSelectionForm()

    print("N" + ": " + str(time.time() - starttime))
    starttime=time.time()


    reverse_side = None
    if photo_obj.back_of is not None:
        reverse_side = photo_obj.back_of
    elif photo_obj.front_of is not None:
        reverse_side = photo_obj.front_of

    seconds = None
    if photo_obj.video_timestamp:
        seconds = photo_obj.video_timestamp / 1000

    print("O" + ": " + str(time.time() - starttime))
    starttime=time.time()

    context = {
        'photo': photo_obj,
        'similar_photos': similar_photos,
        'previous_datings': serialized_datings,
        'datings_count': previous_datings.count(),
        'original_thumb_size': original_thumb_size,
        'user_confirmed_this_location': user_confirmed_this_location,
        'user_has_geotagged': user_has_geotagged,
        'fb_url': "https://facebook.com", #request.build_absolute_uri(reverse('photo', args=(photo_obj.id,))),
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
        'hostname': "https://ajapaik.ee", #request.build_absolute_uri('/'),
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
        'is_photo_modal': False, #request.is_ajax(),
        # TODO: Needs more data than just the names
        'people': people,
        'whole_set_albums_selection_form': whole_set_albums_selection_form,
        'seconds': seconds
    }

    print("P" + ": " + str(time.time() - starttime))
    starttime=time.time()
    t=render(request, template, context)
    print("P1" + ": " + str(time.time() - starttime))
    starttime=time.time()


    print("P2" + ": " + str(time.time() - starttime2))


class Command(BaseCommand):
    help = 'Test photoslug'

    def handle(self, *args, **options):
#        profile = Profile.objects.get(pk=44387121)
        rf = RequestFactory()
        request=get_request = rf.get('/photo/124147/saaremaa-sorve-fire-tower/')

        profile = Profile.objects.get(pk=38)
        test_photoslug(request, 124147, profile)
