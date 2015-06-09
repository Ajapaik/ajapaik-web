from ujson import loads
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache
import requests
from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from sorl.thumbnail import get_thumbnail
import time
from project.home.cat import CustomAuthentication
from project.home.facebook import APP_ID
from project.home.forms import CatLoginForm, ApiAlbumNearestForm, ApiAlbumStateForm, ApiRegisterForm, ApiPhotoUploadForm
from project.home.models import Album, Photo, Profile
from project.settings import API_DEFAULT_NEARBY_PHOTOS_RANGE, API_DEFAULT_NEARBY_MAX_PHOTOS, FACEBOOK_APP_SECRET, \
    GOOGLE_CLIENT_ID


@api_view(['POST'])
@parser_classes((FormParser,))
@permission_classes((AllowAny,))
def api_login(request):
    login_form = CatLoginForm(request.data)
    content = {
        'error': 0,
        'session': None,
        'expires': 86400
    }
    user = None
    if login_form.is_valid():
        t = login_form.cleaned_data['type']
        uname = login_form.cleaned_data['username']
        if t == 'ajapaik' or t == 'auto':
            uname = uname[:30]
        pw = login_form.cleaned_data['password']
        user = None
        if t == 'ajapaik':
            try:
                user = authenticate(username=uname, password=pw)
            except ObjectDoesNotExist:
                pass
        elif t == 'google':
            response = requests.get('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % pw)
            parsed_reponse = loads(response.text)
            try:
                if GOOGLE_CLIENT_ID == parsed_reponse['issued_to'] and parsed_reponse['email'] == uname and parsed_reponse['verified_email']:
                    profile = Profile.objects.filter(google_plus_email=uname).first()
                    if profile:
                        user = profile.user
                        user.backend='django.contrib.auth.backends.ModelBackend'
            except KeyError:
                pass
        elif t == 'facebook':
            response = requests.get('https://graph.facebook.com/debug_token?input_token=%s&access_token=%s' % (pw, APP_ID + '|' + FACEBOOK_APP_SECRET))
            parsed_reponse = loads(response.text)
            try:
                if APP_ID == parsed_reponse['data']['app_id'] and parsed_reponse['data']['is_valid']:
                    fb_user_id = parsed_reponse['data']['user_id']
                    profile = Profile.objects.filter(fb_id=fb_user_id).first()
                    if profile:
                        user = profile.user
                        user.backend='django.contrib.auth.backends.ModelBackend'
            except KeyError:
                pass
        if not user and t == 'auto':
            User.objects.create_user(username=uname, password=pw)
            user = authenticate(username=uname, password=pw)
    else:
        content['error'] = 2
    if user:
        login(request, user)
        content['id'] = user.id
        content['session'] = request.session.session_key
    else:
        content['error'] = 4

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


@api_view(['POST'])
@parser_classes((FormParser,))
@authentication_classes((CustomAuthentication,))
@permission_classes((AllowAny,))
def api_register(request):
    register_form = ApiRegisterForm(request.data)
    content = {
        'error': 0,
        'session': None,
        'expires': 86400
    }
    user = None
    # FIXME: Mostly duplicate code from /login
    if register_form.is_valid():
        t = register_form.cleaned_data['type']
        uname = register_form.cleaned_data['username']
        if t == 'ajapaik' or t == 'auto':
            uname = uname[:30]
        pw = register_form.cleaned_data['password']
        user = None
        if t == 'ajapaik':
            try:
                user = authenticate(username=uname, password=pw)
                profile = user.profile
                profile.merge_from_other(request.user.profile)
            except ObjectDoesNotExist:
                pass
        elif t == 'google':
            response = requests.get('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % pw)
            parsed_reponse = loads(response.text)
            try:
                if GOOGLE_CLIENT_ID == parsed_reponse['issued_to'] and parsed_reponse['email'] == uname and parsed_reponse['verified_email']:
                    profile = Profile.objects.filter(google_plus_email=uname).first()
                    if profile:
                        user = profile.user
                        user.backend='django.contrib.auth.backends.ModelBackend'
                        profile.merge_from_other(request.user.profile)
                        profile.update_from_google_plus_data(parsed_reponse)
            except KeyError:
                pass
        elif t == 'facebook':
            response = requests.get('https://graph.facebook.com/debug_token?input_token=%s&access_token=%s' % (pw, APP_ID + '|' + FACEBOOK_APP_SECRET))
            parsed_reponse = loads(response.text)
            try:
                if APP_ID == parsed_reponse['data']['app_id'] and parsed_reponse['data']['is_valid']:
                    fb_user_id = parsed_reponse['data']['user_id']
                    profile = Profile.objects.filter(fb_id=fb_user_id).first()
                    if profile:
                        user = profile.user
                        user.backend='django.contrib.auth.backends.ModelBackend'
                        profile.merge_from_other(request.user.profile)
                        profile.update_from_fb_data(parsed_reponse['data'])
            except KeyError:
                pass
        if not user and t == 'auto':
            User.objects.create_user(username=uname, password=pw)
            user = authenticate(username=uname, password=pw)
    else:
        content['error'] = 2
    if user:
        login(request, user)
        content['id'] = user.id
        content['session'] = request.session.session_key
    else:
        content['error'] = 4

    return Response(content)


@never_cache
def api_album_thumb(request, album_id, thumb_size=250):
    a = get_object_or_404(Album, id=album_id)
    random_image = a.photos.order_by('?').first()
    if not random_image:
        for sa in a.subalbums.all():
            random_image = sa.order_by('?').first()
            if random_image:
                break
    thumb_str = str(thumb_size) + 'x' + str(thumb_size)
    im = get_thumbnail(random_image.image, thumb_str, upscale=False)
    content = im.read()
    response = HttpResponse(content, content_type='image/jpg')

    return response


@api_view(['POST'])
@parser_classes((FormParser,))
@authentication_classes((CustomAuthentication,))
@permission_classes((IsAuthenticated,))
def api_albums(request):
    error = 0
    albums = Album.objects.filter(is_public=True).order_by('-created')
    ret = []
    content = {}
    for a in albums:
        ret.append({
            'id': a.id,
            'title': a.name,
            'image': request.build_absolute_uri(reverse('project.home.api.api_album_thumb', args=(a.id,))) + '?' + str(time.time()),
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
    content = {
        'state': str(int(round(time.time() * 1000)))
    }
    photos = []
    if form.is_valid():
        album = form.cleaned_data["id"]
        if album:
            content["title"] = album.name
            photos_qs = album.photos.all()
            for sa in album.subalbums.all():
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
        album_nearby_photos = photos_qs.filter(lat__isnull=False, lon__isnull=False, rephoto_of__isnull=True, geography__distance_lte=(ref_location,
            D(m=nearby_range))).distance(ref_location).annotate(rephoto_count=Count('rephotos')).order_by('distance')[:API_DEFAULT_NEARBY_MAX_PHOTOS]
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
                "image": request.build_absolute_uri(reverse("project.home.views.photo_thumb", args=(p.id,))) + '[DIM]/',
                "width": p.width,
                "height": p.height,
                "title": p.description,
                "date": date,
                "author": p.author,
                "source": p.source_url,
                "latitude": p.lat,
                "longitude": p.lon,
                "rephotos": p.rephoto_count
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
    content = {
        'state': str(int(round(time.time() * 1000)))
    }
    photos = []
    if form.is_valid():
        album = form.cleaned_data["id"]
        album_photos_qs = album.photos.filter(rephoto_of__isnull=True)
        for sa in album.subalbums.all():
            album_photos_qs = album_photos_qs | sa.photos.filter(rephoto_of__isnull=True)
        album_photos_qs = album_photos_qs.annotate(rephoto_count=Count('rephotos'))
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
                "image": request.build_absolute_uri(reverse("project.home.views.photo_thumb", args=(p.id,))) + '[DIM]/',
                "width": p.width,
                "height": p.height,
                "title": p.description,
                "date": date,
                "author": p.author,
                "source": p.source_url,
                "latitude": p.lat,
                "longitude": p.lon,
                "rephotos": p.rephoto_count
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
    # id = forms.ModelChoiceField(queryset=Photo.objects.filter(rephoto_of__isnull=True))
    # latitude = forms.FloatField(min_value=-85.05115, max_value=85)
    # longitude = forms.FloatField(min_value=-180, max_value=180)
    # accuracy = forms.FloatField(min_value=0)
    # age = forms.FloatField(min_value=0)
    # date = forms.CharField(max_length=30)
    # scale = forms.FloatField()
    # yaw = forms.FloatField()
    # pitch = forms.FloatField()
    # roll = forms.FloatField()
    # original = forms.FileField()
    upload_form = ApiPhotoUploadForm(request.data, request.FILES)
    content = {
        'state': str(int(round(time.time() * 1000)))
    }
    if upload_form.is_valid():
        print "valid"
    else:
        print upload_form.errors

    return Response(content)