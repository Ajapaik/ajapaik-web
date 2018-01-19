# coding=utf-8
import datetime
import time
import urllib2
import logging
from StringIO import StringIO
from json import loads

import pytz
import requests

from PIL import Image, ExifTags
from dateutil import parser
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point, GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.db.models import Count, Q, Case, When, Value, BooleanField, \
    IntegerField
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import activate
from django.views.decorators.cache import never_cache
from oauth2client import client, crypt
from rest_framework import generics
from rest_framework import authentication, exceptions
from rest_framework.decorators import api_view, permission_classes, \
    authentication_classes, parser_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView, exception_handler
from sorl.thumbnail import get_thumbnail

from project.ajapaik import forms
from project.ajapaik.models import Album, Photo, Profile, Licence, PhotoLike
from project.ajapaik.settings import API_DEFAULT_NEARBY_PHOTOS_RANGE, \
    API_DEFAULT_NEARBY_MAX_PHOTOS, FACEBOOK_APP_SECRET, GOOGLE_CLIENT_ID, \
    FACEBOOK_APP_ID, MEDIA_ROOT, TIME_ZONE
from project.ajapaik import serializers


log = logging.getLogger(__name__)


# Response statuses
RESPONSE_STATUSES = {
    'OK': 0,  # no error
    'UNKNOWN_ERROR': 1,  # unknown error
    'INVALID_PARAMETERS': 2,  # invalid input parameter
    'MISSING_PARAMETERS': 3,  # missing input parameter
    'ACCESS_DENIED': 4,  # access denied
    'SESSION_REQUIRED': 5,  # session is required
    'SESSION_EXPIRED': 6,  # session is expired
    'INVALID_SESSION': 7,  # session is invalid
    'USER_ALREADY_EXISTS': 8,  # user exists in the DB already
    'INVALID_APP_VERSION': 9,  # application version is not supported
    'MISSING_USER': 10,  # user does not exist
    'INVALID_PASSWORD': 11,  # wrong password for existing user
}


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    # TODO: Error handling
    if response is not None:
        response.data['error'] = 7

    return response


class CustomAuthentication(authentication.BaseAuthentication):
    @parser_classes((FormParser,))
    def authenticate(self, request):
        cat_auth_form = forms.APIAuthForm(request.data)
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


class CustomAuthenticationMixin(object):
    authentication_classes = (CustomAuthentication,)
    permission_classes = (IsAuthenticated,)


class CustomParsersMixin(object):
    parser_classes = (FormParser, MultiPartParser,)


@parser_classes((FormParser,))
def login_auth(request, auth_type='login'):
    form = forms.APILoginAuthForm(request.data)
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
                if form.cleaned_data['firstname'] and form.cleaned_data['lastname']:
                    user.first_name = form.cleaned_data['firstname']
                    user.last_name = form.cleaned_data['lastname']
                    user.save()
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
                fb_get_info_url = "https://graph.facebook.com/v2.5/me?fields=%s&access_token=%s" % (
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


class AlbumNearest(CustomAuthenticationMixin, CustomParsersMixin, APIView):
    '''
    API endpoint to retrieve album photos(if album is specified else just
    photos) in specified radius.
    '''
    def post(self, request, format=None):
        form = forms.ApiAlbumNearestForm(request.data)
        if form.is_valid():
            album = form.cleaned_data["id"]
            nearby_range = form.cleaned_data["range"] or API_DEFAULT_NEARBY_PHOTOS_RANGE
            ref_location = Point(
                round(form.cleaned_data["longitude"], 4),
                round(form.cleaned_data["latitude"], 4)
            )
            if album:
                photos = Photo.objects.filter(
                    Q(albums=album)
                    | (Q(albums__subalbum_of=album)
                       & ~Q(albums__atype=Album.AUTO)),
                    rephoto_of__isnull=True
                ).filter(
                    lat__isnull=False,
                    lon__isnull=False,
                    geography__distance_lte=(ref_location, D(m=nearby_range))
                ) \
                    .distance(ref_location) \
                    .order_by('distance')[:API_DEFAULT_NEARBY_MAX_PHOTOS]

                return Response({
                    'error': RESPONSE_STATUSES['OK'],
                    'photos': serializers.AlbumSerializer(
                        instance=album,
                        context={
                            'request': request,
                            'photos': photos
                        }
                    ).data
                })
            else:
                photos = Photo.objects.filter(
                    lat__isnull=False,
                    lon__isnull=False,
                    rephoto_of__isnull=True,
                    geography__distance_lte=(ref_location, D(m=nearby_range))
                ) \
                    .distance(ref_location) \
                    .order_by('distance')[:API_DEFAULT_NEARBY_MAX_PHOTOS]

                photos = serializers.PhotoSerializer.annotate_photos(
                    photos,
                    request.user.profile
                )

                return Response({
                    'error': RESPONSE_STATUSES['OK'],
                    'photos': serializers.PhotoSerializer(
                        instance=photos,
                        many=True,
                        context={'request': request}
                    ).data
                })
        else:
            return Response({
                'error': RESPONSE_STATUSES['INVALID_PARAMETERS'],
                'photos': []
            })


class AlbumDetails(CustomAuthenticationMixin, CustomParsersMixin, APIView):
    '''
    API endpoint to retrieve album details and details of this album photos.
    '''
    def post(self, request, format=None):
        form = forms.ApiAlbumStateForm(request.data)
        if form.is_valid():
            album = form.cleaned_data["id"]
            photos = Photo.objects.filter(
                Q(albums=album)
                | (Q(albums__subalbum_of=album)
                   & ~Q(albums__atype=Album.AUTO)),
                rephoto_of__isnull=True
            )
            response_data = {
                'error': RESPONSE_STATUSES['OK']
            }
            response_data.update(serializers.AlbumSerializer(
                instance=album,
                context={
                    'request': request,
                    'photos': photos
                }
            ).data)
            return Response(response_data)
        else:
            return Response({
                'error': RESPONSE_STATUSES['INVALID_PARAMETERS']
            })


def _crop_image(img, scale_factor):
    new_size = tuple([int(x * scale_factor) for x in img.size])
    left = (img.size[0] - new_size[0]) / 2
    top = (img.size[1] - new_size[1]) / 2
    right = (img.size[0] + new_size[0]) / 2
    bottom = (img.size[1] + new_size[1]) / 2
    img = img.crop((left, top, right, bottom))

    return img


def _fill_missing_pixels(img, scale_factor):
    new_size = tuple([int(x * scale_factor) for x in img.size])
    x0 = (new_size[0] - img.size[0]) / 2
    y0 = (new_size[1] - img.size[1]) / 2
    new_img = Image.new('RGB', new_size, color=(255, 255, 255))
    new_img.paste(img, (x0, y0))

    return new_img


@api_view(['POST'])
@parser_classes((FormParser, MultiPartParser))
@authentication_classes((CustomAuthentication,))
@permission_classes((IsAuthenticated,))
def api_photo_upload(request):
    profile = request.user.profile
    upload_form = forms.ApiPhotoUploadForm(request.data, request.FILES)
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
        parsed_date = parser.parse(upload_form.cleaned_data['date'], dayfirst=True, ignoretz=True)
        # This workaround assumes we're based in a +something timezone, Europe/Tallinn for example,
        # since the date is sent in as a dd-mm-yyyy string, we don't want any timezone-aware magic
        tz = pytz.timezone(TIME_ZONE)
        dt = datetime.datetime.utcnow()
        offset_seconds = tz.utcoffset(dt).seconds
        offset_hours = offset_seconds / 3600.0
        new_rephoto = Photo(
            image_unscaled=upload_form.cleaned_data['original'],
            image=upload_form.cleaned_data['original'],
            rephoto_of=original_photo,
            lat=lat,
            lon=lng,
            date=datetime.datetime(parsed_date.year, parsed_date.month, parsed_date.day, hour=0 + int(offset_hours)),
            geography=geography,
            gps_accuracy=upload_form.cleaned_data['accuracy'],
            gps_fix_age=upload_form.cleaned_data['age'],
            cam_scale_factor=upload_form.cleaned_data['scale'],
            cam_yaw=upload_form.cleaned_data['yaw'],
            cam_pitch=upload_form.cleaned_data['pitch'],
            cam_roll=upload_form.cleaned_data['roll'],
            flip=upload_form.cleaned_data['flip'],
            licence=Licence.objects.filter(url='https://creativecommons.org/licenses/by/2.0/').first(),
            user=profile,
        )
        new_rephoto.light_save()
        img = Image.open(MEDIA_ROOT + '/' + str(new_rephoto.image))
        img_unscaled = Image.open(MEDIA_ROOT + '/' + str(new_rephoto.image_unscaled))
        try:
            image_orientation = img._getexif()[
                next(
                    (key for key, value in ExifTags.TAGS.items() if value == 'Orientation'),
                    None
                )
            ]
        except KeyError:
            image_orientation = None
        if image_orientation == 3:
            img = img.rotate(180, expand=True)
            img_unscaled = img.rotate(180, expand=True)
            img.save(MEDIA_ROOT + '/' + str(new_rephoto.image), 'JPEG', quality=95)
            img_unscaled.save(MEDIA_ROOT + '/' + str(new_rephoto.image_unscaled), 'JPEG', quality=95)
        elif image_orientation == 6:
            img = img.rotate(270, expand=True)
            img_unscaled = img_unscaled.rotate(270, expand=True)
            img.save(MEDIA_ROOT + '/' + str(new_rephoto.image), 'JPEG', quality=95)
            img_unscaled.save(MEDIA_ROOT + '/' + str(new_rephoto.image_unscaled), 'JPEG', quality=95)
        elif image_orientation == 8:
            img = img.rotate(90, expand=True)
            img_unscaled = img_unscaled.rotate(90, expand=True)
            img.save(MEDIA_ROOT + '/' + str(new_rephoto.image), 'JPEG', quality=95)
            img_unscaled.save(MEDIA_ROOT + '/' + str(new_rephoto.image_unscaled), 'JPEG', quality=95)
        if upload_form.cleaned_data['scale']:
            img = Image.open(MEDIA_ROOT + '/' + str(new_rephoto.image))
            rounded_scale = round(float(upload_form.cleaned_data['scale']), 6)
            output_file = StringIO()
            if rounded_scale < 1:
                cropped_image = _crop_image(img, rounded_scale)
                cropped_image.save(output_file, 'JPEG', quality=95)
            elif rounded_scale > 1:
                filled_image = _fill_missing_pixels(img, rounded_scale)
                filled_image.save(output_file, 'JPEG', quality=95)
            new_rephoto.image.delete()
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
    form = forms.ApiUserMeForm(request.data)
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


class PhotoDetails(CustomAuthenticationMixin, CustomParsersMixin, APIView):
    '''
    API endpoint to retrieve photo details.
    '''
    def post(self, request, format=None):
        form = forms.ApiPhotoStateForm(request.data)
        if form.is_valid():
            user_profile = request.user.profile
            photo = Photo.objects.filter(
                pk=form.cleaned_data['id'],
                rephoto_of__isnull=True
            )
            if photo:
                photo = serializers.PhotoSerializer.annotate_photos(
                    photo,
                    request.user.profile
                ).first()
                response_data = {'error': RESPONSE_STATUSES['OK']}
                response_data.update(
                    serializers.PhotoSerializer(
                        instance=photo, context={'request': request}
                    ).data
                )
                return Response(response_data)
            else:
                return Response({
                    'error': RESPONSE_STATUSES['INVALID_PARAMETERS']
                })
        else:
            return Response({
                'error': RESPONSE_STATUSES['INVALID_PARAMETERS']
            })


class ToggleUserFavoritePhoto(CustomAuthenticationMixin, CustomParsersMixin, APIView):
    '''
    API endpoint to un/like photos by user.
    '''
    def post(self, request, format=None):
        form = forms.ApiToggleFavoritePhotoForm(request.data)
        if form.is_valid():
            photo = form.cleaned_data['id']
            is_favorited = form.cleaned_data['favorited']
            user_profile = request.get_user().profile

            if is_favorited:
                try:
                    # User already have this photo in favorites.
                    # Nothing to do here.
                    PhotoLike.objects.get(photo=photo, profile=user_profile)
                except PhotoLike.DoesNotExist:
                    # User haven't this photo in favorites.
                    # Creating like.
                    photo_like = PhotoLike.objects.create(
                        photo=photo, profile=user_profile
                    )
                    photo_like.save()
            else:
                try:
                    # User already have this photo in favorites.
                    # Removing it.
                    photo_like = PhotoLike.objects.get(
                        photo=photo, profile=request.get_user().profile
                    )
                    photo_like.delete()
                except PhotoLike.DoesNotExist:
                    # User haven't this photo in favorites.
                    # Nothing to do here.
                    pass
            return Response({'error': RESPONSE_STATUSES['OK']})
        else:
            return Response({'error': RESPONSE_STATUSES['INVALID_PARAMETERS']})


class UserFavoritePhotoList(CustomAuthenticationMixin, CustomParsersMixin, APIView):
    '''
    API endpoint to retrieve user liked photos sorted by distance to specified
    location.
    '''
    def post(self, request, format=None):
        form = forms.ApiFavoritedPhotosForm(request.data)
        if form.is_valid():
            user_profile = request.get_user().profile
            latitude = form.cleaned_data['latitude']
            longitude = form.cleaned_data['longitude']
            requested_location = GEOSGeometry(
                'POINT({} {})'.format(longitude, latitude),
                srid=4326
            )
            photos = Photo.objects.filter(likes__profile=user_profile) \
                .distance(requested_location) \
                .order_by('distance')
            photos = serializers.PhotoWithDistanceSerializer.annotate_photos(
                photos,
                request.user.profile
            )
            return Response({
                'error': RESPONSE_STATUSES['OK'],
                'photos': serializers.PhotoWithDistanceSerializer(
                    instance=photos, many=True, context={'request': request}
                ).data,
            })
        else:
            return Response({
                'error': RESPONSE_STATUSES['INVALID_PARAMETERS'],
                'photos': [],
            })


class PhotosSearch(CustomAuthenticationMixin, CustomParsersMixin, APIView):
    '''
    API endpoint to search for photos by given phrase.
    '''
    def post(self, request, format=None):
        form = forms.ApiPhotoSearchForm(request.data)
        if form.is_valid():
            search_phrase = form.cleaned_data['query']
            rephotos_only = form.cleaned_data['rephotosOnly']

            search_results = forms.HaystackPhotoSearchForm({
                'q': search_phrase
            }).search()

            photos = Photo.objects.filter(
                id__in=[item.pk for item in search_results],
                rephoto_of__isnull=(not rephotos_only)
            )
            if rephotos_only:
                photos = photos.filter(
                    rephoto_of__isnull=False
                )
            photos = serializers.PhotoSerializer.annotate_photos(
                photos,
                request.user.profile
            )

            return Response({
                'error': RESPONSE_STATUSES['OK'],
                'photos': serializers.PhotoSerializer(
                    instance=photos,
                    many=True,
                    context={'request': request}
                ).data
            })
        else:
            return Response({
                'error': RESPONSE_STATUSES['INVALID_PARAMETERS'],
                'photos': []
            })
