# coding=utf-8
import logging
import sys
import time
import io
import re
from json import loads
from urllib.request import urlopen

import requests
from PIL import Image, ExifTags
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point, GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import activate
from django.views.decorators.cache import never_cache
from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet
# from oauth2client import client, crypt
from rest_framework import authentication, exceptions
from rest_framework.decorators import api_view, permission_classes, \
    authentication_classes, parser_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView, exception_handler
from sorl.thumbnail import get_thumbnail

from allauth.account.adapter import get_adapter
from allauth.account import app_settings as account_app_settings
from allauth.account.forms import SignupForm
from allauth.account.utils import complete_signup
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from google.auth.transport import requests as google_auth_requests
from google.oauth2 import id_token

from ajapaik.ajapaik import forms
from ajapaik.ajapaik import serializers
from ajapaik.ajapaik.curator_drivers.finna import finna_find_photo_by_url
from ajapaik.ajapaik.models import Album, Photo, Profile, Licence, PhotoLike, GeoTag

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


class Login(CustomParsersMixin, APIView):
    '''
    API endpoint to login user.
    '''

    permission_classes = (AllowAny,)

    def _authenticate_by_email(self, email, password):
        '''
        Authenticate user with email and password.
        '''
        user = authenticate(email=email, password=password)
        if user is not None and not user.is_active:
            # We found user but this user is disabled. "authenticate" does't
            # checking is user is disabled(at least in Django 1.8).
            return
        return user

    def _authenticate_with_google(self, request, token):
        '''
        Returns user by ID token that we get from mobile application after user
        authentication there.
        '''
        idinfo = id_token.verify_oauth2_token(
            token, google_auth_requests.Request(), settings.GOOGLE_CLIENT_ID
        )
        adapter = GoogleOAuth2Adapter(request)
        login = adapter.get_provider().sociallogin_from_response(
            request,
            {
                'email': idinfo['email'],
                'family_name': idinfo['family_name'],
                'gender': '',
                'given_name': idinfo['given_name'],
                'id': idinfo['sub'],
                'link': '',
                'locale': idinfo['locale'],
                'name': idinfo['name'],
                'picture': idinfo['picture'],
                'verified_email': idinfo['email_verified'],
            }
        )
        login.state = {
            'auth_params': '',
            'process': 'login',
            'scope': ''
        }
        complete_social_login(request, login)
        return login.user

    def _authenticate_with_facebook(self, request, access_token):
        '''
        Returns user by facebook access_token.
        '''
        adapter = FacebookOAuth2Adapter(request)
        app = adapter.get_provider().get_app(request)
        token = adapter.parse_token({'access_token': access_token})
        token.app = app
        login = adapter.complete_login(request, app, token)
        login.token = token
        login.state = {
            'auth_params': '',
            'process': 'login',
            'scope': ''
        }
        complete_social_login(request, login)
        return login.user

    def post(self, request, format=None):
        form = forms.APILoginForm(request.data)
        if form.is_valid():
            login_type = form.cleaned_data['type']
            if login_type == forms.APILoginForm.LOGIN_TYPE_AJAPAIK:
                email = form.cleaned_data['username']
                password = form.cleaned_data['password']
                if password is None:
                    return Response({
                        'error': RESPONSE_STATUSES['MISSING_PARAMETERS'],
                        'id': None,
                        'session': None,
                        'expires': None,
                    })
                user = self._authenticate_by_email(email, password)
                if user is not None:
                    get_adapter(request).login(request, user)
            elif login_type == forms.APILoginForm.LOGIN_TYPE_GOOGLE:
                id_token = form.cleaned_data['username']
                user = self._authenticate_with_google(request._request,
                                                      id_token)
            elif login_type == forms.APILoginForm.LOGIN_TYPE_FACEBOOK:
                access_token = form.cleaned_data['password']
                user = self._authenticate_with_facebook(request._request,
                                                        access_token)
            elif login_type == forms.APILoginForm.LOGIN_TYPE_AUTO:
                # Deprecated. Keeped for back compatibility.
                user = None

            if user is None:
                # We can't authenticate user with provided data.
                return Response({
                    'error': RESPONSE_STATUSES['MISSING_USER'],
                    'id': None,
                    'session': None,
                    'expires': None,
                })

            if not request.session.session_key:
                request.session.save()

            return Response({
                'error': RESPONSE_STATUSES['OK'],
                'id': user.id,
                'session': request.session.session_key,
                'expires': request.session.get_expiry_age(),
            })
        else:
            return Response({
                'error': RESPONSE_STATUSES['INVALID_PARAMETERS'],
                'id': None,
                'session': None,
                'expires': None,
            })

class Register(CustomParsersMixin, APIView):
    '''
    API endpoint to register user.
    '''

    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        form = forms.APIRegisterForm(request.data)
        if form.is_valid():
            registration_type = form.cleaned_data['type']
            if registration_type == forms.APIRegisterForm.REGISTRATION_TYPE_AJAPAIK:
                email = form.cleaned_data['username']
                password = form.cleaned_data['password']
                firstname = form.cleaned_data['firstname']
                lastname = form.cleaned_data['lastname']

                account_signup_form = SignupForm(data={
                    'email': email,
                    'password1': password,
                    'password2': password,
                })
                if not account_signup_form.is_valid():
                    return Response({
                        'error': RESPONSE_STATUSES['UNKNOWN_ERROR'],
                        'id': None,
                        'session': None,
                        'expires': None,
                    })
                new_user = account_signup_form.save(request._request)

                new_user.first_name = firstname
                new_user.last_name = lastname
                new_user.save()

                complete_signup(
                    request._request,
                    new_user,
                    account_app_settings.EMAIL_VERIFICATION,
                    None
                )
                return Response({
                    'error': RESPONSE_STATUSES['OK'],
                    'id': new_user.id,
                    'session': None,
                    'expires': None,
                })
            else:
                return Response({
                    'error': RESPONSE_STATUSES['INVALID_PARAMETERS'],
                    'id': None,
                    'session': None,
                    'expires': None,
                })
        else:
            return Response({
                'error': RESPONSE_STATUSES['INVALID_PARAMETERS'],
                'id': None,
                'session': None,
                'expires': None,
            })


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
        im = urlopen('http://rlv.zcache.com/doge_sticker-raf4b2dbd11ec4a7992e8bf94601ace75_v9wth_8byvr_512.jpg')
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
            user_profile = request.user.profile
            filter_rule = Q(is_public=True, photos__isnull=False) \
                          | Q(profile=user_profile, atype=Album.CURATED)
        else:
            filter_rule = Q(is_public=True, photos__isnull=False)

        albums = Album.objects \
            .exclude(atype=Album.PERSON) \
            .filter(filter_rule) \
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
        # print >>sys.stderr, ('_get_finna_results: %f, %f, %f, %s, %s' % (lat, lon, distance, query, album) )

        finna_filters = [
            'free_online_boolean:"1"',
            '~format:"0/Place/"',
            '~format:"0/Image/"',
            '~usage_rights_str_mv:"usage_B"',
            '-topic_facet:"ilmakuvat"',
            '-topic_facet:"arkeologia"',
            '-topic_facet:"lentokoneet"',
            '-topic_facet:"ilmakulkuneuvot lentokoneet"',
            '-author_facet:"Koivisto Andreas"',  # Raumalla tulee liikaa kuvia maasta 
            '-author_facet:"Kauppinen Anne"',  # Vantaan ruokakuvat 
            '{!geofilt sfield=location_geo pt=%f,%f d=%f}' % (lat, lon, distance)
        ]

        if album == "1918":
            finna_filters.append('~era_facet:"1918"')

        finna_result_json = requests.get(self.search_url, {
            'lookfor': query,
            'type': 'AllFields',
            'limit': self.page_size,
            'lng': 'en-gb',
            'streetsearch': 1,
            'field[]': ['id', 'title', 'images', 'imageRights', 'authors', 'source', 'geoLocations', 'recordPage',
                        'year', 'summary', 'rawData'],
            'filter[]': finna_filters
        })

        finna_result = finna_result_json.json()
        if 'records' in finna_result:
            return finna_result['records']
        elif distance < 1000:
            return self._get_finna_results(lat, lon, query, album, distance * 100)
        else:
            return []

    def _handle_request(self, data):
        form = forms.ApiFinnaNearestPhotosForm(data)
        if form.is_valid():
            lon = round(form.cleaned_data["longitude"], 4)
            lat = round(form.cleaned_data["latitude"], 4)
            query = form.cleaned_data["query"] or ""
            album = form.cleaned_data["album"] or ""
            if query == "":
                distance = 0.1
            else:
                distance = 100000

            photos = []
            records = self._get_finna_results(lat, lon, query, album, distance)
            for p in records:
                comma = ', '
                authors = []
                if 'authors' in p:
                    if p['authors']['primary']:
                        for k, each in p['authors']['primary'].items():
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

                ir_description = ''
                image_rights = p.get('imageRights', None)
                if image_rights:
                    ir_description = image_rights.get('description')

                title = p.get('title', '')
                if 'rawData' in p and 'title_alt' in p['rawData']:
                    # Title_alt is used by Helsinki city museum
                    title_alt = next(iter(p['rawData']['title_alt'] or []), None)
                    if title < title_alt:
                        title = title_alt
                elif 'rawData' in p and 'geographic' in p['rawData']:
                    # Museovirasto + others
                    title_geo = next(iter(p['rawData']['geographic'] or []), None)
                    if title_geo:
                        title = '%s ; %s' % (title, title_geo)

                # BUG: No date in android app so we add it here to the title text
                year = p.get('year', None)
                if year:
                    title = '%s (%s)' % (title, p.get('year', ''))

                # Coordinate's are disabled because center coordinates aren't good enough
                photo = {
                    'id': 'https://www.finna.fi%s' % p.get('recordPage', None),
                    'image': 'https://www.finna.fi/Cover/Show?id=%s' % p.get('id', None),
                    'height': 768,
                    'width': 583,
                    'title': title,
                    'date': p.get('year', None),
                    'author': comma.join(authors),
                    'source': {
                        'url': 'https://www.finna.fi%s' % p.get('recordPage', None),
                        'name': ir_description
                    },
                    #                    'azimuth':None,
                    #                    'latitude': p.get('latitude', None),
                    #                    'longitude': p.get('longitude', None),
                    'rephotos': [],
                    'favorited': False
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
            nearby_range = form.cleaned_data["range"] or settings.API_DEFAULT_NEARBY_PHOTOS_RANGE
            ref_location = Point(
                round(form.cleaned_data["longitude"], 4),
                round(form.cleaned_data["latitude"], 4)
            )
            start = form.cleaned_data["start"] or 0
            end = start + (form.cleaned_data["limit"] or settings.API_DEFAULT_NEARBY_MAX_PHOTOS)
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
            end = start + (form.cleaned_data["limit"] or settings.API_DEFAULT_NEARBY_MAX_PHOTOS)

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


class SourceDetails(CustomAuthenticationMixin, CustomParsersMixin, APIView):
    '''
    API endpoint to retrieve album details and details of this album photos.
    '''

    permission_classes = (AllowAny,)

    def _handle_request(self, data, request):
        form = forms.ApiAlbumSourceForm(data)
        if form.is_valid():
            query = form.cleaned_data["query"]
            start = form.cleaned_data["start"] or 0
            end = start + (form.cleaned_data["limit"] or settings.API_DEFAULT_NEARBY_MAX_PHOTOS * 1000)

            photos = Photo.objects.filter(
                source_url__contains=query,
                rephoto_of__isnull=True,
                lat__isnull=False,
                lon__isnull=False,
            )[start:end]
            response_data = {
                'error': RESPONSE_STATUSES['OK']
            }

            photos = serializers.PhotoSerializer.annotate_photos(
                photos,
                None
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
    x0 = int((new_size[0] - img.size[0]) / 2)
    y0 = int((new_size[1] - img.size[1]) / 2)
    new_img = Image.new('RGB', new_size, color=(255, 255, 255))
    new_img.paste(img, (x0, y0))

    return new_img


class RephotoUpload(CustomAuthenticationMixin, CustomParsersMixin, APIView):
    '''
    API endpoint to upload rephoto for a photo.
    '''

    def post(self, request, format=None):
        print('rephotoupload', file=sys.stderr)
        form = forms.ApiPhotoUploadForm(request.data, request.FILES)
        if form.is_valid():
            user_profile = request.user.profile
            print('form.isvalid()', file=sys.stderr)
            id = form.cleaned_data['id']
            if id.isdigit():
                id = int(id)
                photo = Photo.objects.filter(
                    pk=id
                ).first()
            else:
                photo = finna_find_photo_by_url(id, user_profile)

            if not photo:
                print('rephotoupload failed', file=sys.stderr)
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

            image_stream = io.BytesIO()
            image_unscaled_stream = io.BytesIO()
            image.save(image_stream, 'JPEG', quality=95)
            image_unscaled.save(image_unscaled_stream, 'JPEG', quality=95)

            print('new_rephoto', file=sys.stderr)
            new_rephoto = Photo(
                image_unscaled=InMemoryUploadedFile(
                    image_unscaled_stream, None, rephoto.name, 'image/jpeg',
                    sys.getsizeof(image_unscaled_stream), None
                ),
                image=InMemoryUploadedFile(
                    image_stream, None, rephoto.name, 'image/jpeg',
                    sys.getsizeof(image_stream), None
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
            print('original_photo', file=sys.stderr)
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


class FetchFinnaPhoto(CustomAuthenticationMixin, CustomParsersMixin, APIView):
    permission_classes = (AllowAny,)

    def _handle_request(self, data, user, request):
        form = forms.ApiFetchFinnaPhoto(data)

        if form.is_valid():
            if user:
               user_profile = user.profile
            else:
               user_profile = None

            id = form.cleaned_data['id']

            # Limit only to Helsinki city museum photos for now
            m = re.search('https:\/\/(hkm\.|www\.)?finna.fi\/Record\/(hkm\..*?)( |\?|#|$)', id)
            if m:
                photo = finna_find_photo_by_url(id, user_profile)
                if photo:
                   return Response({'error': RESPONSE_STATUSES['OK']})
                else:
                   return Response({'error': RESPONSE_STATUSES['INVALID_PARAMETERS']})
        return Response({'error': RESPONSE_STATUSES['INVALID_PARAMETERS']})


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

            if photo:
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
            end = start + (form.cleaned_data["limit"] or settings.API_DEFAULT_NEARBY_MAX_PHOTOS * 5)

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

    def _handle_request(self, data, user, request):
        form = forms.ApiPhotoSearchForm(data)
        if form.is_valid():
            search_phrase = form.cleaned_data['query']
            rephotos_only = form.cleaned_data['rephotosOnly']
            profile=user.profile if user else None

            sqs = SearchQuerySet().models(Photo).filter(content=AutoQuery(search_phrase))

            photos = Photo.objects.filter(
                id__in=[item.pk for item in sqs],
            )
            if rephotos_only:
                photos = photos.filter(
                    rephoto_of__isnull=False
                )
            photos = serializers.PhotoSerializer.annotate_photos(
                photos,
                profile
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


class PhotosInAlbumSearch(CustomAuthenticationMixin, CustomParsersMixin, APIView):
    '''
    API endpoint to search for photos in album by given phrase.
    '''
    permission_classes = (AllowAny,)

    def _handle_request(self, data, user, request):
        form = forms.ApiPhotoInAlbumSearchForm(data)
        if form.is_valid():
            search_phrase = form.cleaned_data['query']
            album = form.cleaned_data['albumId']
            rephotos_only = form.cleaned_data['rephotosOnly']
            profile=user.profile if user else None

            sqs = SearchQuerySet().models(Photo).filter(content=AutoQuery(search_phrase))

            photos = Photo.objects.filter(
                id__in=[item.pk for item in sqs],
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
                profile
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


class UserRephotosSearch(CustomAuthenticationMixin, CustomParsersMixin, APIView):
    '''
    API endpoint to search for rephotos done by user by given search phrase.
    '''

    def post(self, request, format=None):
        form = forms.ApiUserRephotoSearchForm(request.data)
        if form.is_valid():
            search_phrase = form.cleaned_data['query']
            user_profile = request.user.profile

            sqs = SearchQuerySet().models(Photo).filter(content=AutoQuery(search_phrase))

            photos = Photo.objects.filter(
                id__in=[item.pk for item in sqs],
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

            sqs = SearchQuerySet().models(Album).filter(content=AutoQuery(search_phrase))

            albums = Album.objects.filter(
                id__in=[item.pk for item in sqs]
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

# Show Wikidata items as albums
class WikidocsAlbumsSearch(CustomAuthenticationMixin, CustomParsersMixin, APIView):
    '''
    API endpoint to search for albums by given search phrase.
    '''

    search_url='https://tools.wmflabs.org/fiwiki-tools/hkmtools/wikidocs.php';
    permission_classes = (AllowAny,)

    def _handle_request(self, data, user, request):
        form = forms.ApiWikidocsAlbumsSearchForm(data)
        if form.is_valid():
            lon = form.cleaned_data["longitude"]
            lat = form.cleaned_data["latitude"] 
            language = form.cleaned_data["language"] or request.LANGUAGE_CODE 
            query = form.cleaned_data["query"] or ""
            start = form.cleaned_data["start"] or 0
            limit = form.cleaned_data["limit"] or 50

#            user_profile = user.profile or None
            res = requests.get(self.search_url, {
                'lat': lat,
                'lon': lon,
                'search': query,
                'start': 0,
                'limit': limit,
                'language':language
            });
            albums=[];
            for p in res.json():
                try:
                    album = {
                         'id': p.get('id'),
                         'image': p.get('image'),
                         'title': p.get('title'),
                         'lang': p.get('lang'),
                         'search': p.get('lat'),
                         'type': 'wikidocumentaries',
                         'stats': {
                             'rephotos': p.get('rephotos', 0),
                             'total': p.get('total',0),
                         },
                    }
                    albums.append(album)
                except:
                    pass

            return Response({
                'error': RESPONSE_STATUSES['OK'],
                'albums': albums
            })
        else:
            return Response({
                'error': RESPONSE_STATUSES['INVALID_PARAMETERS'],
                'albums': []
            })

    def post(self, request, format=None):
        user = request.user or None
        return self._handle_request(request.data, user, request)

    def get(self, request, format=None):
        user = request.user or None
        return self._handle_request(request.GET, user, request)

# Photos under single Wikidata item id 
class WikidocsAlbumSearch(CustomAuthenticationMixin, CustomParsersMixin, APIView):
    '''
    API endpoint to search for albums by given search phrase.
    '''

    search_url='https://tools.wmflabs.org/fiwiki-tools/hkmtools/wikidocs_qid_album.php';
    permission_classes = (AllowAny,)

    def _handle_request(self, data, user, request):
        form = forms.ApiWikidocsAlbumSearchForm(data)
        if form.is_valid():
            lon = form.cleaned_data["longitude"]
            lat = form.cleaned_data["latitude"] 
            language = form.cleaned_data["language"] or request.LANGUAGE_CODE 
            query = form.cleaned_data["query"] or ""
            id = form.cleaned_data["id"] or ""
            start = form.cleaned_data["start"] or 0
            limit = form.cleaned_data["limit"] or 50

#            user_profile = user.profile or None
            res = requests.get(self.search_url, {
                'lat': lat,
                'lon': lon,
                'search': query,
                'qid': id,
                'start': 0,
                'limit': limit,
                'language':language
            });
            photos=[];
            for p in res.json():
                try:
                # Coordinate's are disabled because center coordinates aren't good enough
                    photo = {
                        'id': p.get('id'),
                        'image': p.get('thumbURL'),
                        'height': 768,
                        'width': 583,
                        'title': p.get('title'),
                        'date': p.get('year'),
                        'author': p.get('authors'),
                        'source': {
                            'url': p.get('infoURL'),
                            'name': p.get('institutions'),
                            'license': p.get('license')
                        },
                        'azimuth':None,
                        'latitude': p.get('latitude', None),
                        'longitude': p.get('longitude', None),
                        'rephotos': [],
                        'favorited': False
                    }
                    photos.append(photo)
                except:
                    pass

            return Response({
                'error': RESPONSE_STATUSES['OK'],
                'photos': photos
            })
        else:
            return Response({
                'error': RESPONSE_STATUSES['INVALID_PARAMETERS'],
                'albums': []
            })

    def post(self, request, format=None):
        user = request.user or None
        return self._handle_request(request.data, user, request)

    def get(self, request, format=None):
        user = request.user or None
        return self._handle_request(request.GET, user, request)



class PhotosWithUserRephotos(CustomAuthenticationMixin, CustomParsersMixin, APIView):
    '''
    API endpoint for getting photos that contains rephotos done by current user.
    '''

    def post(self, request, format=None):
        form = forms.ApiUserRephotosForm(request.data)
        if form.is_valid():
            user_profile = request.user.profile
            start = form.cleaned_data["start"] or 0
            end = start + (form.cleaned_data["limit"] or settings.API_DEFAULT_NEARBY_MAX_PHOTOS * 10)

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
