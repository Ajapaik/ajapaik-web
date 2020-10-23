# coding=utf-8
import logging
import sys
import datetime
import time
import io
import re
import json
from json import loads
from urllib.request import urlopen
from urllib.parse import parse_qs
from urllib.parse import quote
import logging

import requests
from PIL import Image, ExifTags
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point, GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import activate
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet
from rest_framework import authentication, exceptions
from rest_framework.decorators import api_view, permission_classes, \
    authentication_classes, parser_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication 
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

from ajapaik.utils import most_frequent

from ajapaik.ajapaik import forms
from ajapaik.ajapaik import serializers
from ajapaik.ajapaik.curator_drivers.finna import finna_find_photo_by_url
from ajapaik.ajapaik.models import Album, Photo, PhotoSceneSuggestion, Points, Profile, Licence, PhotoLike, PhotoViewpointElevationSuggestion, ProfileDisplayNameChange, ProfileMergeToken, GeoTag, ImageSimilarity, Transcription, TranscriptionFeedback
from ajapaik.ajapaik.socialaccount.providers.wikimedia_commons.views import WikimediaCommonsOAuth2Adapter
from ajapaik.ajapaik.utils import merge_profiles


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

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class Login(APIView):
    '''
    API endpoint to login user.
    '''

    permission_classes = (AllowAny,)
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def _authenticate_by_email(self, request, email, password):
        '''
        Authenticate user with email and password.
        '''
        user = authenticate(request=request, email=email, password=password)
        if user is not None and not user.is_active:
            # We found user but this user is disabled. 'authenticate' doesn't
            # check is user is disabled(at least in Django 1.8).
            return
        return user

    def _authenticate_with_google(self, request, token):
        '''
        Returns user by ID token that we get from mobile application after user
        authentication there.
        '''
        try:
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
        except:
            return None

    def _authenticate_with_wikimedia_commons(self, request, token):
        '''
        Returns user by ID token that we get from mobile application after user
        authentication there.
        '''
        try:
            adapter = WikimediaCommonsOAuth2Adapter(request)
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
        except:
            return None

    def _authenticate_with_facebook(self, request, access_token):
        '''
        Returns user by facebook access_token.
        '''
        try:
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
        except:
            return None

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
                user = self._authenticate_by_email(request, email, password)
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
            elif login_type == forms.APILoginForm.LOGIN_TYPE_WIKIMEDIA_COMMONS:
                # TODO: Finish API endpoint for Wikimedia Commons login
                pass
            elif login_type == forms.APILoginForm.LOGIN_TYPE_AUTO:
                # Deprecated. Kept for backwards compatibility.
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

class Register(APIView):
    '''
    API endpoint to register user.
    '''

    permission_classes = (AllowAny,)
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    
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

class AjapaikAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def _fix_latin1_query_param(self, request, body):
        post=request.POST.copy()
        if request.encoding != 'UTF-8':
            try:
                # If fails then string is not urlencoded
                body=body.decode('ascii')
                try:
                    latin1=parse_qs(body,encoding='latin-1')
                    if ('query' in latin1):
                        post['query']=latin1['query'][0]
                except:
                    # Do nothing
                    print('Latin1 failed')

            except:
                # Do nothing 
                print('Not urlencoded')
        return post

    def _handle_request(self, data, user, request):
        return Response({
            'error': RESPONSE_STATUSES['INVALID_PARAMETERS'],
            'photos': []
        })

    def _reset_session_cookie(self, request):
        if 'sessionid' in request.session.keys():
            session_id=request.session['sessionid']
            s=Session.objects.get(session_key=session_id)
            if not s:
                del request.session['sessionid']
        return request

    def post(self, request, format=None):
        body=request.body
        post=self._fix_latin1_query_param(request, body)
        request=self._reset_session_cookie(request)
        return self._handle_request(post, request.user, request)

    def get(self, request, format=None):
        request=self._reset_session_cookie(request)
        return self._handle_request(request.GET, request.user, request)


class api_logout(AjapaikAPIView):
    def _handle_request(self, data, user, request):
        errorcode = 0 if user.is_authenticated else 2
        logout(request)
        return Response({'error': errorcode})


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


class AlbumList(AjapaikAPIView):
    '''
    API endpoint to get albums that: public and not empty, or albums that
    overseeing by current user(can be empty).
    '''
    def _handle_request(self, data, user, request):
        if user.is_authenticated:
            user_profile = user.profile
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

class FinnaNearestPhotos(AjapaikAPIView):
    '''
    API endpoint to retrieve album photos(if album is specified else just
    photos) in specified radius.
    '''

    search_url = 'https://api.finna.fi/api/v1/search'
    page_size = 50


    def _get_signe_results(self, lat, lon, search_phrase, user, request):
        album = 1

        if search_phrase:
            sqs = SearchQuerySet().models(Photo).filter(content=AutoQuery(search_phrase))
            photos = Photo.objects.filter(
                id__in=[item.pk for item in sqs],
                albums=album,
                rephoto_of__isnull=True
            )
        else:
            ref_location = Point(x=lon, y=lat, srid=4326)
            nearby_range = settings.API_DEFAULT_NEARBY_PHOTOS_RANGE*10
            start = 0
            end = settings.API_DEFAULT_NEARBY_MAX_PHOTOS

            photos = Photo.objects.filter(
                    albums=album,
                    rephoto_of__isnull=True,
                    lat__isnull=False,
                    lon__isnull=False,
                ).annotate(distance=Distance(('geography'), ref_location)) \
                .filter(distance__lte=(D(m=nearby_range))) \
                .order_by('distance')[start:end]

            if not photos:
                photos = Photo.objects.filter(
                    albums=album,
                    rephoto_of__isnull=True,
                    lat__isnull=False,
                    lon__isnull=False,
                    geography__distance_lte=(ref_location, D(m=nearby_range*100))
                ).annotate(distance=Distance(('geography'), ref_location)) \
                 .order_by('distance')[start:end]

        if photos:
            user_profile = user.profile if user.is_authenticated else None 
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
                'error': RESPONSE_STATUSES['OK'],
                'photos': []
            })

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

        if album == '1918':
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

    def _handle_request(self, data, user, request):
        form = forms.ApiFinnaNearestPhotosForm(data)
        if form.is_valid():
            lon = round(form.cleaned_data['longitude'], 4)
            lat = round(form.cleaned_data['latitude'], 4)
            query = form.cleaned_data['query'] or ''
            album = form.cleaned_data['album'] or ''
            if query == '':
                distance = 0.1
            else:
                distance = 100000

            if album=='signebrander':
                return self._get_signe_results(lat, lon, query, user, request)

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
                    'image': 'https://www.finna.fi/Cover/Show?id=%s' % quote(p.get('id', None)),
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
                'foo' : 'bar',
                'photos': []
            })

class AlbumNearestPhotos(AjapaikAPIView):
    '''
    API endpoint to retrieve album photos(if album is specified else just
    photos) in specified radius.
    '''

    def _handle_request(self, data, user, request):
        form = forms.ApiAlbumNearestPhotosForm(data)
        user_profile = user.profile if user.is_authenticated else None 

        if form.is_valid():
            album = form.cleaned_data['id']
            nearby_range = form.cleaned_data['range'] or settings.API_DEFAULT_NEARBY_PHOTOS_RANGE
            ref_location = Point(
                round(form.cleaned_data['longitude'], 4),
                round(form.cleaned_data['latitude'], 4),
                srid=4326
            )
            start = form.cleaned_data['start'] or 0
            end = start + (form.cleaned_data['limit'] or settings.API_DEFAULT_NEARBY_MAX_PHOTOS)
            if album:
                photos = Photo.objects \
                             .filter(
                    Q(albums=album)
                    | (Q(albums__subalbum_of=album)
                       & ~Q(albums__atype=Album.AUTO)),
                    rephoto_of__isnull=True
                ).filter(
                    lat__isnull=False,
                    lon__isnull=False
                ).annotate(distance=Distance(('geography'), ref_location)) \
                .filter(distance__lte=(D(m=nearby_range))) \
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
                ).annotate(distance=Distance(('geography'), ref_location)) \
                .filter(distance__lte=(D(m=nearby_range))) \
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

class AlbumDetails(AjapaikAPIView):
    '''
    API endpoint to retrieve album details and details of this album photos.
    '''

    def _handle_request(self, data, user, request):
        form = forms.ApiAlbumStateForm(data)
        if form.is_valid():
            album = form.cleaned_data['id']
            start = form.cleaned_data['start'] or 0
            end = start + (form.cleaned_data['limit'] or settings.API_DEFAULT_NEARBY_MAX_PHOTOS)

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

class SourceDetails(AjapaikAPIView):
    '''
    API endpoint to retrieve album details and details of this album photos.
    '''

    def _handle_request(self, data, user, request):
        form = forms.ApiAlbumSourceForm(data)
        if form.is_valid():
            query = form.cleaned_data['query']
            start = form.cleaned_data['start'] or 0
            end = start + (form.cleaned_data['limit'] or settings.API_DEFAULT_NEARBY_MAX_PHOTOS * 1000)

            photos = Photo.objects.filter(
                source_url__contains=query,
                rephoto_of__isnull=True,
            )[start:end]

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


class RephotoUpload(APIView):
    '''
    API endpoint to upload rephoto for a photo.
    '''
    permission_classes = (AllowAny,)
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, format=None):
        print('rephotoupload', file=sys.stderr)
        form = forms.ApiPhotoUploadForm(request.POST, request.FILES)

        if not request.user.is_authenticated:
            return Response({
                'error': RESPONSE_STATUSES['ACCESS_DENIED']
            })

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
                exif = image._getexif() or {}  # Returns None if no EXIF data.
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
                    user=user_profile
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

            photos = Photo.objects.filter(pk=photo.id)

            photos = serializers.PhotoSerializer.annotate_photos(
                photos,
                user_profile
            )

            return Response({
                'error': RESPONSE_STATUSES['OK'],
                'id': new_rephoto.pk,
                'photos': serializers.PhotoSerializer(
                    instance=photos,
                    many=True,
                    context={'request': request}
                ).data
            })
        else:
            print('rephotoupload is_valid() fails', file=sys.stderr)
            return Response({
                'error': RESPONSE_STATUSES['INVALID_PARAMETERS'],
            })

class RephotoUploadSettings(AjapaikAPIView):
    '''
    API endpoint for saving rephoto upload settings
    '''
    def post(self, request, format=None):
        try:
            profile = request.user.profile
            profile.wikimedia_commons_rephoto_upload_consent = request.POST['wikimedia_commons_rephoto_upload_consent']
            profile.save()
            return JsonResponse({'message': _('Rephoto upload settings have been saved')})
        except:
            return JsonResponse({'error': _('Something went wrong')}, status=500)

class api_user_me(AjapaikAPIView):
    def _handle_request(self, data, user, request):
        content = {
            'error': 0,
            'state': str(int(round(time.time() * 1000)))
        }

        if user.is_authenticated:
            profile = user.profile
            if profile.is_legit():
                content['name'] = profile.get_display_name
                content['rephotos'] = profile.photos.filter(rephoto_of__isnull=False).count()
                # general_user_leaderboard = Profile.objects.filter(score__gt=0).order_by('-score')
                # general_user_rank = 0
                # for i in range(0, general_user_leaderboard.count()):
                #     if general_user_leaderboard[i].user_id == profile.user_id:
                #         general_user_rank = (i + 1)
                #         break
                # content['rank'] = general_user_rank
                content['rank'] = 0
        return Response(content)


class PhotoDetails(AjapaikAPIView):
    '''
    API endpoint to retrieve photo details.
    '''
    def _handle_request(self, data, user, request):
        form = forms.ApiPhotoStateForm(data)
        if form.is_valid():
            user_profile = user.profile if user.is_authenticated else None
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

class FetchFinnaPhoto(AjapaikAPIView):
    def _handle_request(self, data, user, request):
        form = forms.ApiFetchFinnaPhoto(data)

        if form.is_valid():
            if user.is_authenticated:
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

class ToggleUserFavoritePhoto(AjapaikAPIView):
    '''
    API endpoint to un/like photos by user.
    '''
    permission_classes = (AllowAny,)

    def _handle_request(self, data, user, request):
        form = forms.ApiToggleFavoritePhotoForm(data)

        photo = None

        if form.is_valid(): 
            if user.is_anonymous:
                return Response({'error': RESPONSE_STATUSES['OK']})

            user_profile = user.profile
            id = form.cleaned_data['id']

            id = form.cleaned_data['id']
            if id.isdigit():
                id = int(id)
                photo = Photo.objects.filter(
                    pk=id
                ).first()
            else:
                photo = finna_find_photo_by_url(id, user_profile)

            if user_profile and photo:
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


class UserFavoritePhotoList(AjapaikAPIView):
    '''
    API endpoint to retrieve user liked photos sorted by distance to specified
    location.
    '''

    def _handle_request(self, data, user, request):
        form = forms.ApiFavoritedPhotosForm(data)
        if form.is_valid():
            if user.is_authenticated:
                user_profile = user.profile
                latitude = form.cleaned_data['latitude']
                longitude = form.cleaned_data['longitude']
                start = form.cleaned_data['start'] or 0
                end = start + (form.cleaned_data['limit'] or settings.API_DEFAULT_NEARBY_MAX_PHOTOS * 2)
                ref_location = Point(x=longitude, y=latitude, srid=4326)
                photos = Photo.objects.filter(likes__profile=user_profile).annotate(distance=Distance(('geography'), ref_location)) \
                         .order_by('distance')[start:end]
                photos = serializers.PhotoWithDistanceSerializer.annotate_photos(
                    photos,
                    user.profile
                )
                return Response({
                    'error': RESPONSE_STATUSES['OK'],
                    'photos': serializers.PhotoWithDistanceSerializer(
                        instance=photos, many=True, context={'request': request}
                    ).data,
                })
            else:
                return Response({
                    'error': RESPONSE_STATUSES['OK'],
                    'photos': [],
                }) 
        else:
            return Response({
                'error': RESPONSE_STATUSES['INVALID_PARAMETERS'],
                'photos': [],
            })


class PhotosSearch(AjapaikAPIView):
    '''
    API endpoint to search for photos by given phrase.
    '''

    def _handle_request(self, data, user, request):
        form = forms.ApiPhotoSearchForm(data)
        if form.is_valid():
            lon = form.cleaned_data['longitude'] or None
            lat = form.cleaned_data['latitude'] or None
            search_phrase = form.cleaned_data['query']
            rephotos_only = form.cleaned_data['rephotosOnly']
            profile=user.profile if user.is_authenticated else None

            sqs = SearchQuerySet().models(Photo).filter(content=AutoQuery(search_phrase))

            photos = Photo.objects.filter(
                id__in=[item.pk for item in sqs], back_of__isnull=True
            )
            if rephotos_only:
                photos = photos.filter(
                    rephoto_of__isnull=False
                )

            if lat and lon:
                ref_location = Point(x=lon, y=lat, srid=4326)
                photos=photos.annotate(distance=Distance(('geography'), ref_location)) \
                    .order_by('distance')

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

class PhotosInAlbumSearch(AjapaikAPIView):
    '''
    API endpoint to search for photos in album by given phrase.
    '''

    def _handle_request(self, data, user, request):
        form = forms.ApiPhotoInAlbumSearchForm(data)
        if form.is_valid():
            lon = form.cleaned_data['longitude'] or None
            lat = form.cleaned_data['latitude'] or None
            search_phrase = form.cleaned_data['query']
            album = form.cleaned_data['albumId']
            rephotos_only = form.cleaned_data['rephotosOnly']
            profile=user.profile if user.is_authenticated else None

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


            if lat and lon:
                print('Sorting by distance')
                ref_location = Point(x=lon, y=lat, srid=4326)
                photos=photos.annotate(distance=Distance(('geography'), ref_location)) \
                    .order_by('distance')


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

class UserRephotosSearch(AjapaikAPIView):
    '''
    API endpoint to search for rephotos done by user by given search phrase.
    '''

    def _handle_request(self, data, user, request):
        form = forms.ApiUserRephotoSearchForm(data)
        if form.is_valid():
            if user.is_authenticated:
                lon = form.cleaned_data['longitude'] or None
                lat = form.cleaned_data['latitude'] or None

                search_phrase = form.cleaned_data['query']

                sqs = SearchQuerySet().models(Photo).filter(content=AutoQuery(search_phrase))
                photos = Photo.objects.filter(
                    id__in=[item.pk for item in sqs],
                    rephoto_of__isnull=False,
                    user=user.profile
                )
                if lat and lon:
                    ref_location = Point(x=lon, y=lat, srid=4326)
                    photos=photos.annotate(distance=Distance(('geography'), ref_location)) \
                        .order_by('distance')

                photos = serializers.PhotoSerializer.annotate_photos(
                    photos,
                    user.profile
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
                    'error': RESPONSE_STATUSES['OK'],
                    'photos': []
                })
        else:
            return Response({
                'error': RESPONSE_STATUSES['INVALID_PARAMETERS'],
                'photos': []
            })


class AlbumsSearch(AjapaikAPIView):
    '''
    API endpoint to search for albums by given search phrase.
    '''
    permission_classes = (AllowAny,)
    def _handle_request(self, data, user, request):
        form = forms.ApiAlbumSearchForm(data)
        if form.is_valid():
            search_phrase = form.cleaned_data['query']
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

    def post(self, request, format=None):
        user = request.user or None
        body = request.body
        post = self._fix_latin1_query_param(request, body)

        return self._handle_request(post, user, request)

    def get(self, request, format=None):
        user = request.user or None
        return self._handle_request(request.GET, user, request)


# Show Wikidata items as albums
class WikidocsAlbumsSearch(AjapaikAPIView):
    '''
    API endpoint to search for albums by given search phrase.
    '''

    search_url='https://tools.wmflabs.org/fiwiki-tools/hkmtools/wikidocs.php'

    def _handle_request(self, data, user, request):
        form = forms.ApiWikidocsAlbumsSearchForm(data)
        if form.is_valid():
            lon = form.cleaned_data['longitude']
            lat = form.cleaned_data['latitude'] 
            language = form.cleaned_data['language'] or request.LANGUAGE_CODE 
            query = form.cleaned_data['query'] or ''
            start = form.cleaned_data['start'] or 0
            limit = form.cleaned_data['limit'] or 50

#            user_profile = user.profile or None
            res = requests.get(self.search_url, {
                'lat': lat,
                'lon': lon,
                'search': query,
                'start': start,
                'limit': limit,
                'language':language
            })
            albums=[]
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

# Photos under single Wikidata item id 
class WikidocsAlbumSearch(AjapaikAPIView):
    '''
    API endpoint to search for albums by given search phrase.
    '''

    search_url='https://tools.wmflabs.org/fiwiki-tools/hkmtools/wikidocs_qid_album.php'

    def _handle_request(self, data, user, request):
        form = forms.ApiWikidocsAlbumSearchForm(data)
        if form.is_valid():
            lon = form.cleaned_data['longitude']
            lat = form.cleaned_data['latitude'] 
            language = form.cleaned_data['language'] or request.LANGUAGE_CODE 
            query = form.cleaned_data['query'] or ''
            id = form.cleaned_data['id'] or ''
            start = form.cleaned_data['start'] or 0
            limit = form.cleaned_data['limit'] or 50

            # user_profile = user.profile or None
            res = requests.get(self.search_url, {
                'lat': lat,
                'lon': lon,
                'search': query,
                'qid': id,
                'start': start,
                'limit': limit,
                'language':language
            })
            photos=[]
            for p in res.json():
                try:
                # Coordinates are disabled because center coordinates aren't good enough
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

class PhotosWithUserRephotos(AjapaikAPIView):
    '''
    API endpoint for getting photos that contains rephotos done by current user.
    '''
    def _handle_request(self, data, user, request):

        form = forms.ApiUserRephotosForm(data)
        if form.is_valid():
            if user.is_authenticated:
                lon = form.cleaned_data['longitude'] or None
                lat = form.cleaned_data['latitude'] or None
                start = form.cleaned_data['start'] or 0
                end = start + (form.cleaned_data['limit'] or settings.API_DEFAULT_NEARBY_MAX_PHOTOS * 2)

                photos = Photo.objects.filter(
                    rephotos__user=user.profile
                )

                if lat and lon:
                    ref_location = Point(x=lon, y=lat, srid=4326)
                    photos=photos.annotate(distance=Distance(('geography'), ref_location)) \
                        .order_by('distance')[start:end]
                else:
                    photos=photos.order_by('rephotos__created')[start:end]


                photos = serializers.PhotoSerializer.annotate_photos(
                    photos,
                    user.profile
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
                    'error': RESPONSE_STATUSES['OK'],
                    'photos': []
                })
        else:
            return Response({
                'error': RESPONSE_STATUSES['INVALID_PARAMETERS'],
                'photos': []
            })

class SubmitSimilarPhotos(AjapaikAPIView):
    '''
    API endpoint for posting similar photos.
    '''
    def post(self, request, format=None):
        points = 0
        profile = request.user.profile
        photos = request.POST['photos'].split(',')
        photos2 = request.POST['photos'].split(',')
        confirmed = request.POST['confirmed']
        similarity_type = request.POST['similarity_type']
        if photos is not None:
            for photo in photos:
                if len(photos2) < 2:
                    break
                photos2 = photos2[1:]
                for photo2 in photos2:
                    photo_obj = get_object_or_404(Photo, id=photo)
                    photo_obj2 = get_object_or_404(Photo, id=photo2)
                    if photo_obj == photo_obj2 or photo_obj is None or photo_obj2 is None:
                        return JsonResponse({'status': 400})
                    inputs = [photo_obj,photo_obj2]
                    if confirmed is not None:
                        inputs.append('1')
                    else:
                        inputs.append('0')
                    if similarity_type is not None:
                        inputs.append(similarity_type)
                    if profile is not None:
                        inputs.append(profile.id)
                    points += ImageSimilarity.add_or_update(*inputs)
        return JsonResponse({'points': points})

class Transcriptions(AjapaikAPIView):
    '''
    API endpoint for getting transcriptions for an image.
    '''
    def get(self, request, photo_id, format=None):
        transcriptions = Transcription.objects.filter(photo_id=photo_id).order_by('-created').values()
        ids = transcriptions.values_list('id', flat=True)
        feedback = TranscriptionFeedback.objects.filter(transcription_id__in=ids)
        for transcription in transcriptions:
            transcription['feedback_count'] = 0
            for fb in feedback:
                if fb.transcription_id == transcription['id']:
                    transcription['feedback_count'] +=1
            profile = Profile.objects.filter(user_id=transcription['user_id']).first()
            transcription['user_name'] = profile.get_display_name
        def feedback_count(elem):
            return elem['feedback_count']
        data = { 'transcriptions': sorted(list(transcriptions), key=feedback_count, reverse=True) }
        return JsonResponse(data, safe=False)

    def post(self, request, format=None):
        try:
            photo = get_object_or_404(Photo, id=request.POST['photo'])
            user = get_object_or_404(Profile, pk=request.user.profile.id)
            count = Transcription.objects.filter(photo=photo,text=request.POST['text']).count()
            text = request.POST['text']

            if count < 1:
                previous_transcription_by_current_user = Transcription.objects.filter(photo=photo, user=user).first()
                if previous_transcription_by_current_user:
                    previous_transcription_by_current_user.text = text
                    previous_transcription_by_current_user.save()
                    if not photo.first_transcription:
                        photo.first_transcription = previous_transcription_by_current_user.modified
                    photo.latest_transcription = previous_transcription_by_current_user.modified
                    photo.light_save()
                else:
                    transcription = Transcription(
                        user = user,
                        text = text,
                        photo = photo
                    )
                    transcription.save()
                    TranscriptionFeedback(
                        user=user,
                        transcription=transcription
                    ).save()
                    photo.latest_transcription = transcription.created
                    if not photo.first_transcription:
                        photo.first_transcription = transcription.created
                    photo.transcription_count += 1
                    photo.light_save()

            transcriptionsWithSameText = Transcription.objects.filter(photo=photo,text=text).exclude(user=user)
            upvoted = False
            for transcription in transcriptionsWithSameText:
                TranscriptionFeedback(
                    user=user,
                    transcription=transcription
                ).save()
                upvoted = True
            
            if count > 0:
                if upvoted:
                    return JsonResponse({'message': _('This transcription already exists, previous transcription was upvoted, thank you!')})
                else:
                    return JsonResponse({'message': _('You have already submitted this transcription, thank you!')})
            else:
                if previous_transcription_by_current_user:
                    return JsonResponse({'message': _('Your transcription has been updated, thank you!')})
                else:
                    return JsonResponse({'message': _('Transcription added, thank you!')})
        except:
            return JsonResponse({'error': _('Something went wrong')}, status=500)

class SubmitTranscriptionFeedback(AjapaikAPIView):
    '''
    API endpoint for confirming transcription for an image.
    '''
    def post(self, request, format=None):
        try:
            if TranscriptionFeedback.objects.filter(transcription_id=request.POST['id'], user_id = request.user.profile.id).count() > 0:
                return JsonResponse({'message': _('You have already given feedback for this transcription')})
            else:
                TranscriptionFeedback(
                    user=get_object_or_404(Profile, pk=request.user.profile.id),
                    transcription=get_object_or_404(Transcription, id=request.POST['id'])
                ).save()
                return JsonResponse({'message': _('Transcription feedback added, thank you!')})
        except:
            return JsonResponse({'error': _('Something went wrong')}, status=500)

class UserSettings(AjapaikAPIView):
    '''
    API endpoint for saving user settings
    '''
    def post(self, request, format=None):
        try:
            profile = request.user.profile
            profile.preferred_language = request.POST['preferredLanguage']
            profile.newsletter_consent = request.POST['newsletterConsent']
            profile.save()
            return JsonResponse({'message': _('User settings have been saved')})
        except:
            return JsonResponse({'error': _('Something went wrong')}, status=500)

class ChangeProfileDisplayName(AjapaikAPIView):
    '''
    API endpoint for changing user display name
    '''
    def post(self, request, format=None):
        try:
            profile = request.user.profile
            profile.display_name = request.POST['display_name']
            profile.save()
            profile_display_name_change = ProfileDisplayNameChange(display_name=request.POST['display_name'], profile=profile)
            profile_display_name_change.save()
            return JsonResponse({'message': _('User display name has been saved')})
        except:
            return JsonResponse({'error': _('Something went wrong')}, status=500)

class MergeProfiles(AjapaikAPIView):
    '''
    API endpoint for merging two users' points, photos, annotations, datings, etc..
    '''
    def post(self, request, format=None):
        reverse = request.POST['reverse']
        token = request.POST['token']
        if token is None:
            return JsonResponse({'error': _('Required parameter, token is missing')}, status=400)
        profile_merge_token = ProfileMergeToken.objects.filter(token=token).first()
        if profile_merge_token is None:
            return JsonResponse({'error': _('Invalid token')}, status=401)
        if profile_merge_token.used is not None or (profile_merge_token.created < (timezone.now() - datetime.timedelta(hours=1))):
            return JsonResponse({'error': _('Expired token')}, status=401)
        if request.user and request.user.profile and request.user.profile.is_legit():
            if request.user.profile.id is not profile_merge_token.profile.id:
                if reverse == 'true':
                    merge_profiles(request.user.profile, profile_merge_token.profile)
                    profile_merge_token.target_profile = request.user.profile
                    profile_merge_token.source_profile = profile_merge_token.profile
                else:
                    merge_profiles(profile_merge_token.profile, request.user.profile)
                    profile_merge_token.target_profile = profile_merge_token.profile
                    profile_merge_token.source_profile = request.user.profile
                    login(request, profile_merge_token.profile.user, backend=settings.AUTHENTICATION_BACKENDS[0])
                profile_merge_token.used = datetime.datetime.now()
                profile_merge_token.save()
                return JsonResponse({'message': _('Contributions and settings from the other account were added to current')})
            else:
                return JsonResponse({'message': _('Please login with a different account, you are currently logged in with the same account that you are merging from')})
        else:
            return JsonResponse({'error': _('Please login')}, status=401)

class PhotoSuggestion(AjapaikAPIView):
    '''
    API endpoints for getting photo scene category and updating it
    '''
    def get(self, request, photo_id, format=None):
        try:
            photo = get_object_or_404(Photo, id=photo_id)
            scene = 'undefined'
            scene_consensus = 'undefined'
            viewpoint_elevation = 'undefined'
            viewpoint_elevation_consensus = 'undefined'
            viewpoint_elevation_suggestion = PhotoViewpointElevationSuggestion.objects.filter(photo=photo, proposer=request.user.profile).order_by('-created').first()
            if viewpoint_elevation_suggestion:
                if viewpoint_elevation_suggestion.viewpoint_elevation == 0:
                    viewpoint_elevation = 'Ground'
                if viewpoint_elevation_suggestion.viewpoint_elevation == 1:
                    viewpoint_elevation = 'Raised'
                if viewpoint_elevation_suggestion.viewpoint_elevation == 2:
                    viewpoint_elevation = 'Aerial'


            scene_suggestion = PhotoSceneSuggestion.objects.filter(photo=photo, proposer=request.user.profile).order_by('-created').first()

            if scene_suggestion:
                if scene_suggestion.scene == 0:
                    scene = 'Interior'
                if scene_suggestion.scene == 1:
                    scene = 'Exterior'
            
            if photo.scene == 0:
                scene_consensus = 'Interior'
            if photo.scene == 1:
                scene_consensus = 'Exterior'

            if photo.viewpoint_elevation == 0:
                viewpoint_elevation_consensus = 'Ground'
            if photo.viewpoint_elevation == 1:
                viewpoint_elevation_consensus = 'Raised'
            if photo.viewpoint_elevation == 2:
                viewpoint_elevation_consensus = 'Aerial'
    
            return JsonResponse({'scene': scene, 'scene_consensus': scene_consensus, 'viewpoint_elevation': viewpoint_elevation, 'viewpoint_elevation_consensus': viewpoint_elevation_consensus})
        except:
            return JsonResponse({'error': _('Something went wrong')}, status=500)
    
    def post(self, request, format=None):
        profile = request.user.profile
        data = json.loads(request.body.decode('utf-8'))
        scene = data['scene']
        viewpoint_elevation = data['viewpointElevation']
        
        photo_ids = data['photoIds']
        suggestion_already_exists = _('You have already submitted this suggestion')
        suggestion_saved = _('Your suggestion has been saved')
        suggestion_changed = _('Your suggestion has been changed')

        if (scene is None or scene == 'undefined') and (viewpoint_elevation is None or viewpoint_elevation == 'undefined'):
            return JsonResponse({'error': _('Add at least scene or viewpoint_elevation parameter to the request')}, status=400)

        for photo_id in photo_ids:

            if photo_id is None:
                return JsonResponse({'error': _('Missing parameter photo_id')}, status=400)

            if not photo_id.isdigit():
                return JsonResponse({'error': _('Parameter photo_id must be an positive integer')}, status=400)

            photo = Photo.objects.filter(id=photo_id).first()
            if photo is None:
                return JsonResponse({'error': _('No photo with id:') + ' ' + photo_id}, status=404)

            response = ''

            try:
                if scene:
                    for choice in PhotoSceneSuggestion.SCENE_CHOICES:
                        if choice[1] == scene:
                            previous_suggestion = PhotoSceneSuggestion.objects.filter(photo=photo, proposer=profile).order_by('-created').first()
                            if previous_suggestion is not None and previous_suggestion.scene == choice[0] and response != suggestion_changed and response != suggestion_saved:
                                response = suggestion_already_exists
                            else:
                                new_suggestion = PhotoSceneSuggestion(proposer=profile, photo=photo, scene=choice[0])
                                new_suggestion.save()

                                all_suggestions = PhotoSceneSuggestion.objects.filter(photo=photo).order_by('-created')
                                if all_suggestions is None:
                                    photo.scene = choice[0]
                                    photo.save()
                                else:
                                    suggestion_scenes = []
                                    
                                    for suggestion in all_suggestions:
                                        suggestion_scenes.append(suggestion.scene)

                                    most_common_choice = most_frequent(suggestion_scenes)

                                    photo.scene = most_common_choice
                                    photo.save()

                                if previous_suggestion:
                                    response = suggestion_changed
                                elif response != suggestion_changed:
                                    Points(user=profile, action=Points.CATEGORIZE_SCENE, photo=photo, points=20,created=timezone.now()).save()
                                    response = suggestion_saved
                
                if viewpoint_elevation:
                    for choice in PhotoViewpointElevationSuggestion.VIEWPOINT_ELEVATION_CHOICES:
                        if choice[1] == viewpoint_elevation:
                            previous_suggestion = PhotoViewpointElevationSuggestion.objects.filter(photo=photo, proposer=profile).order_by('-created').first()
                            if previous_suggestion is not None and previous_suggestion.viewpoint_elevation == choice[0] and response != suggestion_changed and response != suggestion_saved:
                                response = suggestion_already_exists
                            else:
                                new_suggestion = PhotoViewpointElevationSuggestion(proposer=profile, photo=photo, viewpoint_elevation=choice[0])
                                new_suggestion.save()

                                all_suggestions = PhotoViewpointElevationSuggestion.objects.filter(photo=photo).order_by('-created')
                                if all_suggestions is None:
                                    photo.viewpoint_elevation = choice[0]
                                    photo.save()
                                else:
                                    suggestion_viewpoint_elevations = []
                                    
                                    for suggestion in all_suggestions:
                                        suggestion_viewpoint_elevations.append(suggestion.viewpoint_elevation)

                                    most_common_choice = most_frequent(suggestion_viewpoint_elevations)

                                    photo.viewpoint_elevation = most_common_choice
                                    photo.save()

                                if previous_suggestion:
                                    response = suggestion_changed
                                elif response != suggestion_changed:
                                    Points(user=profile, action=Points.ADD_VIEWPOINT_ELEVATION, photo=photo, points=20,created=timezone.now()).save()
                                    response = suggestion_saved
            except:
                return JsonResponse({'error': _('Something went wrong')}, status=500)
        return JsonResponse({'message': response})