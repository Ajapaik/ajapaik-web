# encoding: utf-8
from datetime import datetime
import json
import urllib
import urlparse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from sorl.thumbnail import get_thumbnail
from project.home.forms import CatLoginForm
from project.home.models import CatAlbum, CatTagPhoto, CatPhoto
from rest_framework import authentication
from rest_framework import exceptions


class CustomAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        body_data = urlparse.parse_qsl(urllib.unquote(request.body))
        bullshit = {}
        for item in body_data:
            bullshit[item[0]] = item[1]
        try:
            session_data = eval(bullshit['session'])
        except KeyError:
            raise exceptions.AuthenticationFailed('No user/session')
        user_id = session_data['_u']
        session_id = session_data['_s']
        if not session_id or not user_id:
            return None
        try:
            session = Session.objects.get(session_key=session_id)
            user = User.objects.get(pk=user_id)
        except (User.DoesNotExist, Session.DoesNotExist):
            raise exceptions.AuthenticationFailed('No user/session')

        return user, None


@api_view(['POST'])
@authentication_classes((CustomAuthentication,))
@permission_classes((IsAuthenticated,))
def cat_albums(request):
    error = 0
    albums = CatAlbum.objects.all().order_by('-created')
    ret = []
    for a in albums:
        user_tagged_all_in_album = \
            a.photos.count() == CatTagPhoto.objects.filter(profile=request.get_user().profile).distinct('photo').count()
        if user_tagged_all_in_album:
            user_tagged_all_in_album = 1
        else:
            user_tagged_all_in_album = 0
        ret.append({
            'id': a.id,
            'title': a.title,
            'subtitle': a.subtitle,
            'image': request.build_absolute_uri(reverse('project.home.cat.cat_album_thumb', args=(a.id, 250))),
            'tagged': user_tagged_all_in_album
        })
    content = {
        'error': error,
        'albums': ret
    }
    return Response(content)


@api_view(['POST'])
@permission_classes((AllowAny,))
def cat_login(request):
    body_data = urlparse.parse_qsl(urllib.unquote(request.body))
    bullshit = {}
    for item in body_data:
        bullshit[item[0]] = item[1]
    login_form = CatLoginForm(bullshit)
    error = 0
    user = None
    session = None
    if login_form.is_valid():
        user = authenticate(
            username=login_form.cleaned_data['username'],
            password=login_form.cleaned_data['password']
        )
        if not user and login_form.cleaned_data['type'] == 'auto':
            User.objects.create_user(
                username=login_form.cleaned_data['username'],
                password=login_form.cleaned_data['password']
            )
            user = authenticate(
                username=login_form.cleaned_data['username'],
                password=login_form.cleaned_data['password']
            )
    else:
        error = 2
    if user:
        login(request, user)
        session = request.session.session_key
    else:
        error = 4
    content = {
        'error': error,
        'session': session,
        'expires': 0
    }
    if user:
        content['id'] = user.id
    return Response(content)


@api_view(['POST'])
@authentication_classes((CustomAuthentication,))
@permission_classes((IsAuthenticated,))
def cat_logout(request):
    body_data = urlparse.parse_qsl(urllib.unquote(request.body))
    bullshit = {}
    for item in body_data:
        bullshit[item[0]] = item[1]
    try:
        session_data = eval(bullshit['session'])
    except KeyError:
        raise exceptions.AuthenticationFailed('No user/session')
    session_id = session_data['_s']
    try:
        Session.objects.get(pk=session_id).delete()
    except ObjectDoesNotExist:
        pass
    return Response({'error': 0})


def cat_album_thumb(request, album_id, thumb_size=150):
    cache_key = "ajapaik_cat_album_thumb_response_%s_%s" % (album_id, thumb_size)
    cached_response = cache.get(cache_key)
    if cached_response:
        return cached_response
    a = get_object_or_404(CatAlbum, id=album_id)
    thumb_str = str(thumb_size) + 'x' + str(thumb_size)
    im = get_thumbnail(a.image, thumb_str, upscale=False)
    content = im.read()
    next_week = datetime.datetime.now() + datetime.timedelta(seconds=604800)
    response = HttpResponse(content, content_type='image/jpg')
    response['Content-Length'] = len(content)
    response['Cache-Control'] = "max-age=604800, public"
    response['Expires'] = next_week.strftime("%a, %d %b %y %T GMT")
    cache.set(cache_key, response)
    return response

