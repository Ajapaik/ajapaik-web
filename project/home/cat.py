# encoding: utf-8
import time
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes, permission_classes, parser_classes
from rest_framework.parsers import FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import exception_handler
from sorl.thumbnail import get_thumbnail
from project.home.forms import CatLoginForm, CatAuthForm, CatAlbumStateForm, CatTagForm
from project.home.models import CatAlbum, CatTagPhoto, CatPhoto, CatTag
from rest_framework import authentication
from rest_framework import exceptions
import random


class CustomAuthentication(authentication.BaseAuthentication):
    @parser_classes((FormParser,))
    def authenticate(self, request):
        try:
            cat_auth_form = CatAuthForm(eval(request.data['session']))
        except KeyError:
            raise exceptions.AuthenticationFailed('No user/session')
        user = None
        if cat_auth_form.is_valid():
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


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    # TODO: Error handling
    if response is not None:
        response.data['error'] = 1

    return response


@api_view(['POST'])
@parser_classes((FormParser,))
@permission_classes((AllowAny,))
def cat_login(request):
    login_form = CatLoginForm(request.data)
    content = {
        'error': 0,
        'session': None,
        'expires': 0
    }
    user = None
    if login_form.is_valid():
        uname = login_form.cleaned_data['username']
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
def cat_logout(request):
    try:
        session_data = eval(request.data['session'])
    except KeyError:
        return Response({'error': 4})
    session_id = session_data['_s']
    try:
        Session.objects.get(pk=session_id).delete()
        return Response({'error': 0})
    except ObjectDoesNotExist:
        return Response({'error': 2})


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


def _get_album_state(request, form):
    content = {
        'error': 0,
        'photos': [],
        'state': int(round(time.time() * 1000))
    }
    if form.is_valid():
        all_cat_tags = list(CatTag.objects.order_by('?').values_list('name', flat=True))
        count = len(all_cat_tags)
        album = form.cleaned_data['id']
        content['title'] = album.title
        content['subtitle'] = album.subtitle
        content['image'] = request.build_absolute_uri(reverse('project.home.cat.cat_album_thumb', args=(album.id, 400)))
        for p in album.photos.all():
            content['photos'].append({
                'id': p.id,
                'image': request.build_absolute_uri(reverse('project.home.cat.cat_photo', args=(p.id, 400))),
                'title': p.title,
                'author': p.author,
                'source': {'source1': {'name': p.source.description, 'url': p.source_url}},
                'tag': random.sample(all_cat_tags, count)
            })
    else:
        content['error'] = 2

    return content


@api_view(['POST'])
@parser_classes((FormParser,))
@authentication_classes((CustomAuthentication,))
@permission_classes((IsAuthenticated,))
def cat_album_state(request):
    cat_album_state_form = CatAlbumStateForm(request.data)
    return Response(_get_album_state(request, cat_album_state_form))


def cat_photo(request, photo_id, thumb_size=600):
    cache_key = "ajapaik_cat_photo_response_%s_%s" % (photo_id, thumb_size)
    cached_response = cache.get(cache_key)
    if cached_response:
        return cached_response
    p = get_object_or_404(CatPhoto, id=photo_id)
    thumb_str = str(thumb_size) + 'x' + str(thumb_size)
    im = get_thumbnail(p.image, thumb_str, upscale=False)
    content = im.read()
    next_week = datetime.datetime.now() + datetime.timedelta(seconds=604800)
    response = HttpResponse(content, content_type='image/jpg')
    response['Content-Length'] = len(content)
    response['Cache-Control'] = "max-age=604800, public"
    response['Expires'] = next_week.strftime("%a, %d %b %y %T GMT")
    cache.set(cache_key, response)

    return response


@api_view(['POST'])
@parser_classes((FormParser,))
@authentication_classes((CustomAuthentication,))
@permission_classes((IsAuthenticated,))
def cat_tag(request):
    cat_tag_form = CatTagForm(request.data)
    content = _get_album_state(request, cat_tag_form)
    if cat_tag_form.is_valid():
        CatTagPhoto(
            tag=cat_tag_form.cleaned_data['tag'],
            photo=cat_tag_form.cleaned_data['photo'],
            profile=request.get_user().profile,
            value=cat_tag_form.cleaned_data['value']
        ).save()
    else:
        content['error'] = 2

    return Response(content)


@api_view(['POST'])
@parser_classes((FormParser,))
@authentication_classes((CustomAuthentication,))
@permission_classes((IsAuthenticated,))
def user_me(request):
    profile = request.get_user().profile
    content = {
        'error': 0,
        'tagged': CatTagPhoto.objects.filter(profile=profile).distinct('photo').count(),
        'message': 'Lakkuge panni!',
        'link': 'http://i.ytimg.com/vi/yWy_irUVXGU/hqdefault.jpg',
    }

    return Response(content)