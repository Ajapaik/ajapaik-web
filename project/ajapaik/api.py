# coding=utf-8
import time
import urllib2
from StringIO import StringIO
from json import loads

import requests
from PIL import Image
from dateutil import parser
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import activate
from django.views.decorators.cache import never_cache
from oauth2client import client, crypt
from rest_framework import authentication, exceptions
from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import exception_handler
from sorl.thumbnail import get_thumbnail

from project.ajapaik.forms import ApiAlbumNearestForm, ApiAlbumStateForm, ApiPhotoUploadForm, \
    ApiUserMeForm, ApiPhotoStateForm, APIAuthForm, APILoginAuthForm
from project.ajapaik.models import Album, Photo, Profile, Licence
from project.ajapaik.settings import API_DEFAULT_NEARBY_PHOTOS_RANGE, API_DEFAULT_NEARBY_MAX_PHOTOS, \
    FACEBOOK_APP_SECRET, GOOGLE_CLIENT_ID, FACEBOOK_APP_ID, MEDIA_ROOT


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    # TODO: Error handling
    if response is not None:
        response.data['error'] = 7

    return response


class CustomAuthentication(authentication.BaseAuthentication):
    @parser_classes((FormParser,))
    def authenticate(self, request):
        cat_auth_form = APIAuthForm(request.data)
        user = None
        if cat_auth_form.is_valid():
            lang = cat_auth_form.cleaned_data['_l']
            if lang:
                activate(lang)
            user_id = cat_auth_form.cleaned_data['_u']
            session_id = cat_auth_form.cleaned_data['_s']
            if not session_id or not user_id:
                return None
            try:
                Session.objects.get(session_key=session_id)
                user = User.objects.get(pk=user_id)
            except (User.DoesNotExist, Session.DoesNotExist):
                raise exceptions.AuthenticationFailed('No user/session')

        return user, None


@parser_classes((FormParser,))
def login_auth(request, auth_type='login'):
    form = APILoginAuthForm(request.data)
    content = {
        'error': 0,
        'session': None,
        'expires': 86400
    }
    user = None

    if form.is_valid():
        t = form.cleaned_data['type']
        uname = form.cleaned_data['username']
        if t == 'ajapaik' or t == 'auto':
            # Why do not using some validators?
            uname = uname[:30]
        pw = form.cleaned_data['password']

        if t == 'ajapaik':
            num_same_users = User.objects.filter(username=uname).count()
            if auth_type == 'register':
                if num_same_users > 0:
                    # user exists in the DB already
                    content['error'] = 8
                    return content
                User.objects.create_user(username=uname, password=pw)
            elif num_same_users == 0:
                # user does not exists
                content['error'] = 10
                return content

            user = authenticate(username=uname, password=pw)
            if user:
                # For register
                profile = user.profile
            elif auth_type == 'login':
                # user exists but password is incorrect
                content['error'] = 11
                return content

        elif t == 'auto':
            num_same_users = User.objects.filter(username=uname).count()
            if num_same_users == 0:
                User.objects.create_user(username=uname, password=pw)

            user = authenticate(username=uname, password=pw)
            if user:
                profile = user.profile
                profile.merge_from_other(request.get_user().profile)
            else:
                # user exists but password is incorrect
                content['error'] = 11
                return content

        elif t == 'google':
            # response = requests.get('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % pw)

            try:
                idinfo = client.verify_id_token(pw, GOOGLE_CLIENT_ID)

                if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                    raise crypt.AppIdentityError("Wrong issuer.")

            except crypt.AppIdentityError:
                content['error'] = 11
                return content

            profile = Profile.objects.filter(google_plus_email=uname).first()
            if profile:
                request_profile = request.get_user().profile
                if request.user and request.user.is_authenticated():
                    profile.merge_from_other(request_profile)

                user = profile.user
                request.set_user(user)
            else:
                user = request.get_user()
                profile = user.profile

            user.backend = 'django.contrib.auth.backends.ModelBackend'
            # headers = {'Authorization': 'Bearer ' + pw}
            # user_info = requests.get('https://www.googleapis.com/oauth2/v1/userinfo', headers=headers)
            idinfo['id'] = idinfo['sub']
            profile.update_from_google_plus_data(pw, idinfo)

        elif t == 'fb':
            # response = requests.get('https://graph.facebook.com/debug_token?input_token=%s&access_token=%s' % (pw, APP_ID + '|' + FACEBOOK_APP_SECRET))
            response = requests.get('https://graph.facebook.com/debug_token?input_token=%s&access_token=%s' % (
            pw, FACEBOOK_APP_ID + '|' + FACEBOOK_APP_SECRET))
            parsed_reponse = loads(response.text)
            if FACEBOOK_APP_ID == parsed_reponse.get('data', {}).get('app_id') and parsed_reponse.get('data', {}).get(
                    'is_valid'):
                fb_user_id = parsed_reponse['data']['user_id']
                profile = Profile.objects.filter(fb_id=fb_user_id).first()
                if profile:
                    request_profile = request.get_user().profile
                    if request.user and request.user.is_authenticated():
                        profile.merge_from_other(request_profile)

                    user = profile.user
                    request.set_user(user)
                else:
                    user = request.get_user()
                    profile = user.profile

                user.backend = 'django.contrib.auth.backends.ModelBackend'
                fb_permissions = ['id', 'name', 'first_name', 'last_name', 'link', 'email']
                fb_get_info_url = "https://graph.facebook.com/v2.3/me?fields=%s&access_token=%s" % (
                ','.join(fb_permissions), pw)
                user_info = requests.get(fb_get_info_url)
                profile.update_from_fb_data(pw, loads(user_info.text))

            else:
                content['error'] = 11
                return content

        if not user and t == 'auto':
            User.objects.create_user(username=uname, password=pw)
            user = authenticate(username=uname, password=pw)

        if auth_type == 'register' and request.user:
            profile.merge_from_other(request.user.profile)
            if t == 'google':
                profile.update_from_google_plus_data(parsed_reponse)
            elif t == 'facebook':
                profile.update_from_fb_data(parsed_reponse['data'])
    else:
        content['error'] = 2
        return content

    if user:
        login(request, user)
        content['id'] = user.id

        if not request.session.session_key:
            request.session.save()
        content['session'] = request.session.session_key
    else:
        content['error'] = 4

    return content


@api_view(['POST'])
@parser_classes((FormParser,))
@permission_classes((AllowAny,))
def api_login(request):
    content = login_auth(request)
    return Response(content)


@api_view(['POST'])
@parser_classes((FormParser,))
@authentication_classes((CustomAuthentication,))
@permission_classes((AllowAny,))
def api_register(request):
    content = user = login_auth(request, 'register')
    return Response(content)


@api_view(['POST'])
@parser_classes((FormParser,))
@authentication_classes((CustomAuthentication,))
@permission_classes((IsAuthenticated,))
def api_logout(request):
    try:
        session_id = request.data['_s']
    except KeyError:
        return Response({'error': 4})
    try:
        Session.objects.get(pk=session_id).delete()
        return Response({'error': 0})
    except ObjectDoesNotExist:
        return Response({'error': 2})


@never_cache
@permission_classes((AllowAny,))
def api_album_thumb(request, album_id, thumb_size=250):
    a = get_object_or_404(Album, id=album_id)
    random_image = a.photos.order_by('?').first()
    if not random_image:
        for sa in a.subalbums.exclude(atype=Album.AUTO):
            random_image = sa.photos.order_by('?').first()
            if random_image:
                break
    size_str = str(thumb_size)
    thumb_str = size_str + 'x' + size_str
    try:
        im = get_thumbnail(random_image.image, thumb_str, upscale=False)
    except AttributeError:
        im = urllib2.urlopen('http://rlv.zcache.com/doge_sticker-raf4b2dbd11ec4a7992e8bf94601ace75_v9wth_8byvr_512.jpg')
    content = im.read()
    response = HttpResponse(content, content_type='image/jpg')

    return response


@api_view(['POST'])
@parser_classes((FormParser,))
@authentication_classes((CustomAuthentication,))
@permission_classes((IsAuthenticated,))
def api_albums(request):
    error = 0
    albums = Album.objects.filter(
        Q(is_public=True) | Q(profile=request.get_user().profile, atype=Album.CURATED)).order_by('-created')
    ret = []
    content = {}
    for a in albums:
        ret.append({
            'id': a.id,
            'title': a.name,
            'image': request.build_absolute_uri(
                reverse('project.ajapaik.api.api_album_thumb', args=(a.id,))) + '?' + str(time.time()),
            'stats': {
                'total': a.photo_count_with_subalbums,
                'rephotos': a.rephoto_count_with_subalbums
            }
        })
    content['error'] = error
    content['albums'] = ret

    return Response(content)


@api_view(['POST'])
@parser_classes((FormParser,))
@authentication_classes((CustomAuthentication,))
@permission_classes((IsAuthenticated,))
def api_album_nearest(request):
    form = ApiAlbumNearestForm(request.data)
    profile = request.user.profile
    content = {
        'state': str(int(round(time.time() * 1000)))
    }
    photos = []
    if form.is_valid():
        album = form.cleaned_data["id"]
        if album:
            content["title"] = album.name
            photos_qs = album.photos.all()
            for sa in album.subalbums.exclude(atype=Album.AUTO):
                photos_qs = photos_qs | sa.photos.filter()
        else:
            photos_qs = Photo.objects.all()
        lat = round(form.cleaned_data["latitude"], 4)
        lon = round(form.cleaned_data["longitude"], 4)
        ref_location = Point(lon, lat)
        if form.cleaned_data["range"]:
            nearby_range = form.cleaned_data["range"]
        else:
            nearby_range = API_DEFAULT_NEARBY_PHOTOS_RANGE
        album_nearby_photos = photos_qs.filter(lat__isnull=False, lon__isnull=False, rephoto_of__isnull=True,
                                               geography__distance_lte=(ref_location,
                                                                        D(m=nearby_range))).distance(
            ref_location).annotate(rephoto_count=Count('rephotos')).order_by('distance')[:API_DEFAULT_NEARBY_MAX_PHOTOS]
        for p in album_nearby_photos:
            date = None
            if p.date:
                iso = p.date.isoformat()
                date_parts = iso.split('T')[0].split('-')
                date = date_parts[2] + '-' + date_parts[1] + '-' + date_parts[0]
            elif p.date_text:
                date = p.date_text
            photos.append({
                "id": p.id,
                "image": request.build_absolute_uri(
                    reverse("project.ajapaik.views.image_thumb", args=(p.id,))) + '[DIM]/',
                "width": p.width,
                "height": p.height,
                "title": p.description,
                "date": date,
                "author": p.author,
                "source": {'name': p.source.description + ' ' + p.source_key, 'url': p.source_url} if p.source else {
                    'url': p.source_url},
                "latitude": p.lat,
                "longitude": p.lon,
                "rephotos": p.rephoto_count,
                "uploads": p.rephotos.filter(user=profile).count(),
            })
        content["photos"] = photos
    else:
        content["error"] = 2

    return Response(content)


@api_view(['POST'])
@parser_classes((FormParser,))
@authentication_classes((CustomAuthentication,))
@permission_classes((IsAuthenticated,))
def api_album_state(request):
    form = ApiAlbumStateForm(request.data)
    profile = request.user.profile
    content = {
        'state': str(int(round(time.time() * 1000)))
    }
    photos = []
    if form.is_valid():
        album = form.cleaned_data["id"]
        content['title'] = album.name
        album_photos_qs = album.photos.filter(rephoto_of__isnull=True)
        for sa in album.subalbums.exclude(atype=Album.AUTO):
            album_photos_qs = album_photos_qs | sa.photos.filter(rephoto_of__isnull=True)
        album_photos_qs = album_photos_qs.prefetch_related('rephotos').annotate(rephoto_count=Count('rephotos'))
        for p in album_photos_qs:
            date = None
            if p.date:
                iso = p.date.isoformat()
                date_parts = iso.split('T')[0].split('-')
                date = date_parts[2] + '-' + date_parts[1] + '-' + date_parts[0]
            elif p.date_text:
                date = p.date_text
            photos.append({
                "id": p.id,
                "image": request.build_absolute_uri(
                    reverse("project.ajapaik.views.image_thumb", args=(p.id,))) + '[DIM]/',
                "width": p.width,
                "height": p.height,
                "title": p.description,
                "date": date,
                "author": p.author,
                "source": {'name': p.source.description + ' ' + p.source_key, 'url': p.source_url} if p.source else {
                    'url': p.source_url},
                "latitude": p.lat,
                "longitude": p.lon,
                "rephotos": p.rephoto_count,
                "uploads": p.rephotos.filter(user=profile).count(),
            })
        content["photos"] = photos
    else:
        content["error"] = 2

    return Response(content)


@api_view(['POST'])
@parser_classes((FormParser, MultiPartParser))
@authentication_classes((CustomAuthentication,))
@permission_classes((IsAuthenticated,))
def api_photo_upload(request):
    profile = request.user.profile
    upload_form = ApiPhotoUploadForm(request.data, request.FILES)
    content = {
        'error': 0
    }
    if upload_form.is_valid():
        original_photo = upload_form.cleaned_data['id']
        lat = upload_form.cleaned_data['latitude']
        lng = upload_form.cleaned_data['longitude']
        geography = None
        if lat and lng:
            geography = Point(x=lng, y=lat, srid=4326)
        # TODO: Image scaling etc
        new_rephoto = Photo(
            image_unscaled=upload_form.cleaned_data['original'],
            image=upload_form.cleaned_data['original'],
            rephoto_of=original_photo,
            lat=lat,
            lon=lng,
            geography=geography,
            gps_accuracy=upload_form.cleaned_data['accuracy'],
            gps_fix_age=upload_form.cleaned_data['age'],
            date=parser.parse(upload_form.cleaned_data['date']),
            cam_scale_factor=upload_form.cleaned_data['scale'],
            cam_yaw=upload_form.cleaned_data['yaw'],
            cam_pitch=upload_form.cleaned_data['pitch'],
            cam_roll=upload_form.cleaned_data['roll'],
            flip=upload_form.cleaned_data['flip'],
            licence=Licence.objects.filter(url='https://creativecommons.org/licenses/by-sa/4.0/').first(),
            user=profile,
        )
        new_rephoto.light_save()
        if upload_form.cleaned_data['scale']:
            rounded_scale = round(float(upload_form.cleaned_data['scale']), 6)
            img = Image.open(MEDIA_ROOT + '/' + str(new_rephoto.image))
            new_size = tuple([int(x * rounded_scale) for x in img.size])
            output_file = StringIO()
            if rounded_scale < 1:
                x0 = (img.size[0] - new_size[0]) / 2
                y0 = (img.size[1] - new_size[1]) / 2
                x1 = img.size[0] - x0
                y1 = img.size[1] - y0
                new_img = img.transform(new_size, Image.EXTENT, (x0, y0, x1, y1))
                new_img.save(output_file, 'JPEG', quality=95)
                new_rephoto.image.save(str(new_rephoto.image), ContentFile(output_file.getvalue()))
            elif rounded_scale > 1:
                x0 = (new_size[0] - img.size[0]) / 2
                y0 = (new_size[1] - img.size[1]) / 2
                new_img = Image.new('RGB', new_size)
                new_img.paste(img, (x0, y0))
                new_img.save(output_file, 'JPEG', quality=95)
                new_rephoto.image.save(str(new_rephoto.image), ContentFile(output_file.getvalue()))
        content['id'] = new_rephoto.pk
        original_photo.latest_rephoto = new_rephoto.created
        if not original_photo.first_rephoto:
            original_photo.first_rephoto = new_rephoto.created
        original_photo.light_save()
        profile.update_rephoto_score()
        profile.save()
    else:
        content['error'] = 2

    return Response(content)


@api_view(['POST'])
@parser_classes((FormParser,))
@authentication_classes((CustomAuthentication,))
@permission_classes((IsAuthenticated,))
def api_user_me(request):
    profile = request.user.profile
    content = {
        'error': 0,
        'state': str(int(round(time.time() * 1000)))
    }
    form = ApiUserMeForm(request.data)
    if form.is_valid():
        content['name'] = profile.get_display_name()
        content['rephotos'] = profile.photos.filter(rephoto_of__isnull=False).count()
        general_user_leaderboard = Profile.objects.filter(score__gt=0).order_by('-score')
        general_user_rank = 0
        for i in range(0, len(general_user_leaderboard)):
            if general_user_leaderboard[i].user_id == profile.user_id:
                general_user_rank = (i + 1)
                break
        content['rank'] = general_user_rank
    else:
        content['error'] = 2

    return Response(content)


@api_view(['POST'])
@parser_classes((FormParser,))
@authentication_classes((CustomAuthentication,))
@permission_classes((IsAuthenticated,))
def api_photo_state(request):
    form = ApiPhotoStateForm(request.data)
    profile = request.user.profile
    if form.is_valid():
        p = form.cleaned_data['id']
        # FIXME: DRY
        date = None
        if p.date:
            iso = p.date.isoformat()
            date_parts = iso.split('T')[0].split('-')
            date = date_parts[2] + '-' + date_parts[1] + '-' + date_parts[0]
        elif p.date_text:
            date = p.date_text
        content = {
            'id': p.id,
            'image': request.build_absolute_uri(reverse('project.ajapaik.views.image_thumb', args=(p.id,))) + '[DIM]/',
            'width': p.width,
            'height': p.height,
            'title': p.description,
            'date': date,
            'author': p.author,
            'source': {'name': p.source.description + ' ' + p.source_key, 'url': p.source_url},
            'latitude': p.lat,
            'longitude': p.lon,
            'rephotos': p.rephotos.count(),
            'uploads': p.rephotos.filter(user=profile).count(),
            'error': 0
        }
    else:
        content = {
            'error': 2
        }

    return Response(content)
