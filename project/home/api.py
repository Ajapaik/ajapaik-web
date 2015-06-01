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
from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from rest_framework.parsers import FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from sorl.thumbnail import get_thumbnail
import time
from project.home.cat import CustomAuthentication
from project.home.forms import CatLoginForm, ApiAlbumNearestForm
from project.home.models import Album, Photo
from project.settings import API_DEFAULT_NEARBY_PHOTOS_RANGE, API_DEFAULT_NEARBY_MAX_PHOTOS


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
        uname = login_form.cleaned_data['username'][:30]
        pw = login_form.cleaned_data['password']
        try:
            user = authenticate(username=uname, password=pw)
        except ObjectDoesNotExist:
            pass
        if not user and login_form.cleaned_data['type'] == 'auto':
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
@authentication_classes((CustomAuthentication,))
@permission_classes((IsAuthenticated,))
def api_albums(request):
    error = 0
    albums = Album.objects.filter(is_public=True).prefetch_related('photos').order_by('-created')
    album_photos_dict = { x.id: {
        'photos': list(x.photos.all().values_list('id', flat=True)),
        'rephotos': list(x.photos.filter(rephoto_of__isnull=False).values_list('id', flat=True))
    } for x in albums }
    ret = []
    content = {}
    for a in albums:
        if a.subalbum_of_id in album_photos_dict:
            album_photos_dict[a.subalbum_of_id]['photos'] += album_photos_dict[a.id]['photos']
            album_photos_dict[a.subalbum_of_id]['rephotos'] += album_photos_dict[a.id]['rephotos']
    for a in albums:
        ret.append({
            'id': a.id,
            'title': a.name,
            'image': request.build_absolute_uri(reverse('project.home.api.api_album_thumb', args=(a.id,))) + '?' + str(time.time()),
            'stats': {
                'total': len(set(album_photos_dict[a.id]['photos'])),
                'rephotos': len(set(album_photos_dict[a.id]['rephotos']))
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
            photos_qs = album.photos.filter()
            for sa in album.subalbums.all():
                photos_qs = photos_qs | sa.photos.filter()
        else:
            photos_qs = Photo.geo.all()
        lat = form.cleaned_data["latitude"]
        lon = form.cleaned_data["longitude"]
        if form.cleaned_data["range"]:
            nearby_range = form.cleaned_data["range"]
        else:
            nearby_range = API_DEFAULT_NEARBY_PHOTOS_RANGE
        ref_location = Point(lon, lat)
        print nearby_range
        album_nearby_photos = photos_qs.filter(rephoto_of__isnull=True, geography__distance_lte=(ref_location,
            D(m=nearby_range))).distance(ref_location).annotate(rephoto_count=Count('rephotos')).order_by('distance')[:API_DEFAULT_NEARBY_MAX_PHOTOS]
        for p in album_nearby_photos:
            date = None
            if p.date:
                date = p.date.strftime('%d-%m-%Y')
            photos.append({
                "id": p.id,
                "image": request.build_absolute_uri(reverse("project.home.views.photo_thumb", args=(p.id,))) + '[DIM]/',
                "width": p.width,
                "height": p.height,
                "title": p.description,
                "distance": p.distance.m,
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