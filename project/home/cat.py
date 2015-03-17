# encoding: utf-8
from datetime import datetime
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from sorl.thumbnail import get_thumbnail
from project.home.forms import CatLoginForm
from project.home.models import CatAlbum, CatTagPhoto, CatPhoto


@csrf_exempt
def cat_login(request):
    login_form = CatLoginForm(request.POST)
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
    return HttpResponse(json.dumps({
        'id': user.id,
        'error': error,
        'session': session,
        'expires': 0
    }), content_type="application/json")


@csrf_exempt
def cat_logout(request):
    logout(request)
    return HttpResponse(json.dumps({
        'error': 0
    }), content_type="application/json")


@login_required
@csrf_exempt
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
            'image': reverse('project.home.cat.cat_album_thumb', args=(a.id, 250)),
            'tagged': user_tagged_all_in_album
        })
    return HttpResponse(json.dumps({
        'error': error,
        'albums': json.dumps(ret)
    }), content_type="application/json")


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