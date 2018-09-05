# coding=utf-8
import logging
import time
import urllib2
from StringIO import StringIO
from json import loads

import requests
from PIL import Image, ExifTags
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point, GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Q, Count, Case, When, Value
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import activate
from django.views.decorators.cache import never_cache
from oauth2client import client, crypt
from rest_framework import authentication, exceptions
from rest_framework.decorators import api_view, permission_classes, \
    authentication_classes, parser_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView, exception_handler
from sorl.thumbnail import get_thumbnail

from project.ajapaik import forms
from project.ajapaik import serializers
from project.ajapaik.models import Album, Photo, Profile, Licence, PhotoLike, GeoTag
from project.ajapaik.settings import API_DEFAULT_NEARBY_PHOTOS_RANGE, \
    API_DEFAULT_NEARBY_MAX_PHOTOS, FACEBOOK_APP_SECRET, GOOGLE_CLIENT_ID, \
    FACEBOOK_APP_ID

import sys
from project.ajapaik.curator_drivers.finna import finna_find_photo_by_url

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


class AlbumList(CustomAuthenticationMixin, CustomParsersMixin, APIView):
    '''
    API endpoint to get albums that: public and not empty, or albums that
    overseeing by current user(can be empty).
    '''

    permission_classes = (AllowAny,)
    def _handle_request(self, data, request):
        if request.user:
            user_profile=request.user.profile
            filter_rule = Q(is_public=True, photos__isnull=False) \
                          | Q(profile=user_profile, atype=Album.CURATED)
        else:
            filter_rule = Q(is_public=True, photos__isnull=False)

        albums = Album.objects\
            .filter(filter_rule)\
            .order_by('-created')
        albums = serializers.AlbumDetailsSerializer.annotate_albums(albums)

        return Response({
            'error': RESPONSE_STATUSES['OK'],
            'albums': serializers.AlbumDetailsSerializer(
                instance=albums,
                many=True,
                context={'request': request}
            ).data
        })

    def post(self, request, format=None):
        return self._handle_request(request.data, request)

    def get(self, request, format=None):
        return self._handle_request(request.GET, request)


class FinnaNearestPhotos(CustomAuthenticationMixin, CustomParsersMixin, APIView):
    '''
    API endpoint to retrieve album photos(if album is specified else just
    photos) in specified radius.
    '''

    permission_classes = (AllowAny,)
    search_url = 'https://api.finna.fi/api/v1/search'
    page_size = 50

    def _get_finna_results(self, lat, lon, query, album, distance):
        print >>sys.stderr, ('_get_finna_results: %f, %f, %f, %s, %s' % (lat, lon, distance, query, album) )

        finna_filters = [
            'free_online_boolean:"1"',
            '~format:"0/Place/"',
            '~format:"0/Image/"',
            '~usage_rights_str_mv:"usage_B"',
            '-author_facet:"Koivisto Andreas"',  # Raumalla tulee liikaa kuvia maasta 
            '{!geofilt sfield=location_geo pt=%f,%f d=%f}' % (lat, lon, distance)
        ]

        if album == "1918":
            finna_filters.append('~era_facet:"1918"')


        finna_result_json=requests.get(self.search_url, {
            'lookfor': query,
            'type': 'AllFields',
            'limit': self.page_size,
            'lng': 'en-gb',
            'streetsearch' : 1,
            'field[]': ['id', 'title', 'images', 'imageRights', 'authors', 'source', 'geoLocations', 'recordPage',
                        'year', 'summary', 'rawData'],
            'filter[]': finna_filters
        })

        finna_result=finna_result_json.json()
        if 'records' in finna_result:
           return finna_result['records']
        elif distance < 1000:
           return self._get_finna_results(lat, lon, query, album, distance*100)
        else:
           return []

    def _handle_request(self, data):
        form = forms.ApiFinnaNearestPhotosForm(data)
        if form.is_valid():
            lon=round(form.cleaned_data["longitude"], 4)
            lat=round(form.cleaned_data["latitude"], 4)
            query=form.cleaned_data["query"] or ""
            album=form.cleaned_data["album"] or ""
            if query == "":
               distance=0.1
            else:
               distance=100000


            photos=[]
            records=self._get_finna_results(lat, lon, query, album, distance)
            for p in records:
                comma=', '
                authors=[]
                if 'authors' in p:
                    if p['authors']['primary']:
                        for k,each in p['authors']['primary'].items():
                            authors.append(k)

                if 'geoLocations' in p:
                    for each in p['geoLocations']:
                        if 'POINT' in each:
                            point_parts = each.split(' ')
                            lon = point_parts[0][6:]
                            lat = point_parts[1][:-1]
                            try:
                                p['longitude'] = float(lon)
                                p['latitude'] = float(lat)
                                break
                            except:
                                p['longitude'] = None
                                p['latitude'] = None

                ir_description=''
                image_rights=p.get('imageRights', None)
                if image_rights :
                    ir_description=image_rights.get('description')

                title=p.get('title', '')
                if 'rawData' in p and 'title_alt' in p['rawData']:
                    # Title_alt is used by Helsinki city museum
                    title_alt=next(iter(p['rawData']['title_alt'] or []), None)
                    if title < title_alt:
                        title=title_alt
                elif 'rawData' in p and 'geographic' in p['rawData']:
                    # Museovirasto + others
                    title_geo=next(iter(p['rawData']['geographic'] or []), None)
                    if title_geo :
                        title='%s ; %s' % (title, title_geo)

                # BUG: No date in android app so we add it here to the title text
                year = p.get('year', None)
                if year:
                    title = '%s (%s)' % (title, p.get('year', ''))

                # Coordinate's are disabled because center coordinates aren't good enough
                photo= {
                    'id':'https://www.finna.fi%s' % p.get('recordPage', None),
                    'image':'https://www.finna.fi/Cover/Show?id=%s' % p.get('id', None) ,
                    'height':768,
                    'width':583,
                    'title':title,
                    'date':p.get('year', None),
                    'author':comma.join(authors),
                    'source': {
                                  'url': 'https://www.finna.fi%s' % p.get('recordPage', None),
                                  'name': ir_description
                              },
#                    'azimuth':None,
#                    'latitude': p.get('latitude', None),
#                    'longitude': p.get('longitude', None),
                    'rephotos':[],
                    'favorited':False
                }
                photos.append(photo)


            return Response({
                'error': RESPONSE_STATUSES['OK'],
                'photos': photos
            })
        else:
            return Response({
                'error': RESPONSE_STATUSES['INVALID_PARAMETERS'],
                'photos': []
            })
        return HttpResponse(response, content_type="application/json")

    def post(self, request, format=None):
        return self._handle_request(request.data)

    def get(self, request, format=None):
        return self._handle_request(request.GET)

class AlbumNearestPhotos(CustomAuthenticationMixin, CustomParsersMixin, APIView):
    '''
    API endpoint to retrieve album photos(if album is specified else just
    photos) in specified radius.
    '''

    permission_classes = (AllowAny,)
    def _handle_request(self, data, user, request):
        form = forms.ApiAlbumNearestPhotosForm(data)
        user_profile = user.profile if user else None

        if form.is_valid():
            album = form.cleaned_data["id"]
            nearby_range = form.cleaned_data["range"] or API_DEFAULT_NEARBY_PHOTOS_RANGE
            ref_location = Point(
                round(form.cleaned_data["longitude"], 4),
                round(form.cleaned_data["latitude"], 4)
            )
            start = form.cleaned_data["start"] or 0
            end = start + ( form.cleaned_data["limit"] or API_DEFAULT_NEARBY_MAX_PHOTOS )
            if album:
                photos = Photo.objects \
                    .filter(
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
                    .order_by('distance')[start:end]

#                    .filter(
#                        Q(likes__profile=user_profile) | Q(likes__isnull=True)
#                    ) \

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
                photos = Photo.objects \
                    .filter(
                        lat__isnull=False,
                        lon__isnull=False,
                        rephoto_of__isnull=True,
                        geography__distance_lte=(ref_location, D(m=nearby_range))
                    ) \
                    .distance(ref_location) \
                    .order_by('distance')[start:end]

                photos = serializers.PhotoSerializer.annotate_photos(
                    photos,
                    user_profile
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

    def post(self, request, format=None):
        user = request.user or None
        return self._handle_request(request.data, user, request)

    def get(self, request, format=None):
        user = request.user or None
        return self._handle_request(request.GET, user, request)



class AlbumDetails(CustomAuthenticationMixin, CustomParsersMixin, APIView):
    '''
    API endpoint to retrieve album details and details of this album photos.
    '''

    permission_classes = (AllowAny,)
    def _handle_request(self, data, request):
        form = forms.ApiAlbumStateForm(data)
        if form.is_valid():
            album = form.cleaned_data["id"]
            start = form.cleaned_data["start"] or 0
            end = start + ( form.cleaned_data["limit"] or API_DEFAULT_NEARBY_MAX_PHOTOS )

            photos = Photo.objects.filter(
                Q(albums=album)
                | (Q(albums__subalbum_of=album)
                   & ~Q(albums__atype=Album.AUTO)),
                rephoto_of__isnull=True
            )[start:end]
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

    def post(self, request, format=None):
        return self._handle_request(request.data, request)

    def get(self, request, format=None):
        return self._handle_request(request.GET, request)


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


class RephotoUpload(CustomAuthenticationMixin, CustomParsersMixin, APIView):
    '''
    API endpoint to upload rephoto for a photo.
    '''

    def post(self, request, format=None):
        print >>sys.stderr, ('rephotoupload')
        form = forms.ApiPhotoUploadForm(request.data, request.FILES)
        if form.is_valid():
            user_profile = request.user.profile

            print >>sys.stderr, ('form.isvalid()')
            id = form.cleaned_data['id']
            if id.isdigit():
                id = int(id)
                photo = Photo.objects.filter(
                    pk=id
                ).first()
            else:
                photo = finna_find_photo_by_url(id, user_profile)

            if not photo:
                print >>sys.stderr, ('rephotoupload failed')
                return Response({
                    'error': RESPONSE_STATUSES['INVALID_PARAMETERS'],
                })
            
 
            original_photo = photo
            latitude = form.cleaned_data['latitude']
            longitude = form.cleaned_data['longitude']
            rephoto = form.cleaned_data['original']
            date = form.cleaned_data['date']
            coordinate_accuracy = form.cleaned_data['accuracy']
            coordinates_age = form.cleaned_data['age']
            scale_factor = form.cleaned_data['scale']
            device_yaw = form.cleaned_data['yaw']
            device_pitch = form.cleaned_data['pitch']
            device_roll = form.cleaned_data['roll']
            is_rephoto_flipped = form.cleaned_data['flip']

            geography = None
            if latitude and longitude:
                geography = Point(x=longitude, y=latitude, srid=4326)
            licence = Licence.objects.get(id=17)  # CC BY 4.0

            image = Image.open(rephoto.file)

            if hasattr(image, '_getexif'):  # Present only in JPEGs.
                exif = image._getexif() or {}  # Reterns None if no EXIF data.
                image_orientation = exif.get(
                    next(
                        (
                            key for key, value in ExifTags.TAGS.items()
                            if value == 'Orientation'
                        ),
                        None
                    )
                )
                if image_orientation == 2:
                    image = image.transpose(Image.FLIP_LEFT_RIGHT)
                elif image_orientation in [3, 4]:
                    image = image.rotate(180, expand=True)
                    if image_orientation == 4:
                        image = image.transpose(Image.FLIP_LEFT_RIGHT)
                elif image_orientation in [5, 6]:
                    image = image.rotate(-90, expand=True)
                    if image_orientation == 5:
                        image = image.transpose(Image.FLIP_LEFT_RIGHT)
                elif image_orientation in [7, 8]:
                    image = image.rotate(90, expand=True)
                    if image_orientation == 7:
                        image = image.transpose(Image.FLIP_LEFT_RIGHT)

            image_unscaled = image
            if scale_factor and scale_factor < 1:
                image = _crop_image(image, scale_factor)
            elif scale_factor and scale_factor > 1:
                image = _fill_missing_pixels(image, scale_factor)

            image_stream = StringIO()
            image_unscaled_stream = StringIO()
            image.save(image_stream, 'JPEG', quality=95)
            image_unscaled.save(image_unscaled_stream, 'JPEG', quality=95)

            print >>sys.stderr, ('new_rephoto')
            new_rephoto = Photo(
                image_unscaled=InMemoryUploadedFile(
                    image_unscaled_stream, None, rephoto.name, 'image/jpeg',
                    image_unscaled_stream.len, None
                ),
                image=InMemoryUploadedFile(
                    image_stream, None, rephoto.name, 'image/jpeg',
                    image_stream.len, None
                ),
                rephoto_of=original_photo,
                lat=latitude,
                lon=longitude,
                date=date,
                geography=geography,
                gps_accuracy=coordinate_accuracy,
                gps_fix_age=coordinates_age,
                cam_scale_factor=scale_factor,
                cam_yaw=device_yaw,
                cam_pitch=device_pitch,
                cam_roll=device_roll,
                flip=is_rephoto_flipped,
                licence=licence,
                user=user_profile,
            )
            new_rephoto.save()
            print >>sys.stderr, ('original_photo')

            original_photo.latest_rephoto = new_rephoto.created
            if not original_photo.first_rephoto:
                original_photo.first_rephoto = new_rephoto.created

            if latitude and longitude:
                rephoto_geotag = GeoTag(
                    lat=latitude,
                    lon=longitude,
                    origin=GeoTag.REPHOTO,
                    type=GeoTag.ANDROIDAPP,
                    map_type=GeoTag.NO_MAP,
                    photo=original_photo,
                    trustworthiness=0,
                    is_correct=False,
                    geography=geography,
                    photo_flipped=is_rephoto_flipped,
                )
                rephoto_geotag.save()
                # Investigate why this will always set geotag.is_correct=True 
                original_photo.set_calculated_fields()
                original_photo.latest_geotag = new_rephoto.created
                for a in original_photo.albums.all():
                    qs = a.get_geotagged_historic_photo_queryset_with_subalbums()
                    a.geotagged_photo_count_with_subalbums = qs.count()
                    a.save()

            original_photo.save()
            user_profile.update_rephoto_score()
            user_profile.save()
            return Response({
                'error': RESPONSE_STATUSES['OK'],
                'id': new_rephoto.pk,
            })
        else:
            return Response({
                'error': RESPONSE_STATUSES['INVALID_PARAMETERS'],
            })


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
    permission_classes = (AllowAny,)
    def _handle_request(self, data, user, request):
        form = forms.ApiPhotoStateForm(data)
        if form.is_valid():
            user_profile = user.profile if user else None
            photo = Photo.objects.filter(
                pk=form.cleaned_data['id'],
                rephoto_of__isnull=True
            )
            if photo:
                photo = serializers.PhotoSerializer.annotate_photos(
                    photo,
                    user_profile
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

    def post(self, request, format=None):
        user = request.user or None
        return self._handle_request(request.data, user, request)

    def get(self, request, format=None):
        user = request.user or None
        return self._handle_request(request.GET, user, request)

class ToggleUserFavoritePhoto(CustomAuthenticationMixin, CustomParsersMixin, APIView):
    '''
    API endpoint to un/like photos by user.
    '''

    def post(self, request, format=None):
        form = forms.ApiToggleFavoritePhotoForm(request.data)

        photo = None

        if form.is_valid():
            user_profile = request.user.profile
            id = form.cleaned_data['id']

            if id.isdigit():
                id = int(id)
                photo = Photo.objects.filter(
                    pk=id
                ).first()
            else:
                photo = finna_find_photo_by_url(id, user_profile)

            if photo :
                is_favorited = form.cleaned_data['favorited']

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
                            photo=photo, profile=user_profile
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
            start = form.cleaned_data["start"] or 0
            end = start + ( form.cleaned_data["limit"] or API_DEFAULT_NEARBY_MAX_PHOTOS*5 )

            requested_location = GEOSGeometry(
                'POINT({} {})'.format(longitude, latitude),
                srid=4326
            )
            photos = Photo.objects.filter(likes__profile=user_profile) \
                .distance(requested_location) \
                .order_by('distance')[start:end]
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

    permission_classes = (AllowAny,)

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


class PhotosInAlbumSearch(CustomAuthenticationMixin, CustomParsersMixin, APIView):
    '''
    API endpoint to search for photos in album by given phrase.
    '''

    def post(self, request, format=None):
        form = forms.ApiPhotoInAlbumSearchForm(request.data)
        if form.is_valid():
            search_phrase = form.cleaned_data['query']
            album = form.cleaned_data['albumId']
            rephotos_only = form.cleaned_data['rephotosOnly']

            search_results = forms.HaystackPhotoSearchForm({
                'q': search_phrase
            }).search()

            photos = Photo.objects.filter(
                id__in=[item.pk for item in search_results],
                albums=album
            )
            if rephotos_only:
                # Rephotos only.
                photos = photos.filter(rephoto_of__isnull=False)
            else:
                # Old photos only.
                photos = photos.filter(rephoto_of__isnull=True)
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


class UserRephotosSearch(CustomAuthenticationMixin, CustomParsersMixin, APIView):
    '''
    API endpoint to search for rephotos done by user by given search phrase.
    '''

    def post(self, request, format=None):
        form = forms.ApiUserRephotoSearchForm(request.data)
        if form.is_valid():
            search_phrase = form.cleaned_data['query']
            user_profile = request.user.profile

            search_results = forms.HaystackPhotoSearchForm({
                'q': search_phrase
            }).search()

            photos = Photo.objects.filter(
                id__in=[item.pk for item in search_results],
                rephoto_of__isnull=False,
                user=user_profile
            )
            photos = serializers.PhotoSerializer.annotate_photos(
                photos,
                user_profile
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


class AlbumsSearch(CustomAuthenticationMixin, CustomParsersMixin, APIView):
    '''
    API endpoint to search for albums by given search phrase.
    '''

    def post(self, request, format=None):
        form = forms.ApiAlbumSearchForm(request.data)
        if form.is_valid():
            search_phrase = form.cleaned_data['query']
            user_profile = request.user.profile

            search_results = forms.HaystackAlbumSearchForm({
                'q': search_phrase
            }).search()

            albums = Album.objects.filter(
                id__in=[item.pk for item in search_results]
            )
            albums = serializers.AlbumDetailsSerializer.annotate_albums(albums)

            return Response({
                'error': RESPONSE_STATUSES['OK'],
                'albums': serializers.AlbumDetailsSerializer(
                    instance=albums,
                    many=True,
                    context={'request': request}
                ).data
            })
        else:
            return Response({
                'error': RESPONSE_STATUSES['INVALID_PARAMETERS'],
                'albums': []
            })


class PhotosWithUserRephotos(CustomAuthenticationMixin, CustomParsersMixin, APIView):
    '''
    API endpoint for getting photos that contains rephotos done by current user.
    '''

    def post(self, request, format=None):
        form = forms.ApiUserRephotosForm(request.data)
        if form.is_valid():
            user_profile = request.user.profile
            start = form.cleaned_data["start"] or 0
            end = start + ( form.cleaned_data["limit"] or API_DEFAULT_NEARBY_MAX_PHOTOS*10 )

            photos = Photo.objects.filter(
                     rephotos__user=user_profile
                 ).order_by('created')[start:end]

            photos = serializers.PhotoSerializer.annotate_photos(
                photos,
                user_profile
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
