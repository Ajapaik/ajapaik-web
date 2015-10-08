# encoding: utf-8
from copy import deepcopy
import time
import datetime
import random
from ujson import dumps

from django.utils.translation import activate
from django.views.decorators.cache import never_cache
from django.views.decorators.vary import vary_on_headers
import operator
from pytz import utc
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes, parser_classes
from rest_framework.parsers import FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import exception_handler
from sorl.thumbnail import get_thumbnail, delete
from django.core.cache import cache
from rest_framework import authentication
from rest_framework import exceptions
from django.utils.translation import ugettext as _

from project.sift.forms import CatLoginForm, CatAuthForm, CatAlbumStateForm, CatTagForm, CatFavoriteForm, CatResultsFilteringForm, \
    CatPushRegisterForm, HaystackCatPhotoSearchForm
from project.sift.models import CatAlbum, CatTagPhoto, CatPhoto, CatTag, CatUserFavorite, CatPushDevice, CatProfile
from project.ajapaik.models import Photo
from project.sift.serializers import CatResultsPhotoSerializer
from project.sift.forms import CatTaggerAlbumSelectionForm
from project.sift.settings import SITE_ID, CAT_RESULTS_PAGE_SIZE


class CustomAuthentication(authentication.BaseAuthentication):
    @parser_classes((FormParser,))
    def authenticate(self, request):
        cat_auth_form = CatAuthForm(request.data)
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


class AnonymousUserPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user:
            user = request.get_user()
        return user.is_authenticated()


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    # TODO: Error handling
    if response is not None:
        response.data['error'] = 7

    return response


@api_view(['POST'])
@parser_classes((FormParser,))
@permission_classes((AllowAny,))
def cat_login(request):
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
        # Django 1.7.10 doesn't allow empty sessions
        Session(session_key=content['session'], session_data='Lulz',
                expire_date=datetime.datetime.now() + datetime.timedelta(seconds=content['expires'])).save()
    else:
        content['error'] = 4
    return Response(content)


@api_view(['POST'])
@parser_classes((FormParser,))
@authentication_classes((CustomAuthentication,))
@permission_classes((IsAuthenticated,))
def cat_logout(request):
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
def cat_album_thumb(request, album_id, thumb_size=250):
    a = CatAlbum.objects.filter(pk=album_id).first()
    random_image = a.photos.order_by('?').first()
    thumb_str = str(thumb_size) + 'x' + str(thumb_size)
    im = get_thumbnail(random_image.image, thumb_str, upscale=False)
    try:
        content = im.read()
    except IOError:
        delete(im)
        im = get_thumbnail(random_image.image, thumb_str, upscale=False)
        content = im.read()
    response = HttpResponse(content, content_type='image/jpg')

    return response


@api_view(['POST'])
@authentication_classes((SessionAuthentication, CustomAuthentication))
@permission_classes((AnonymousUserPermission, IsAuthenticated))
def cat_albums(request):
    error = 0
    albums = CatAlbum.objects.all().order_by('-created')
    ret = []
    profile = request.user.profile
    all_tags = CatTagPhoto.objects.all()
    all_distinct_profile_tags = all_tags.distinct('profile')
    general_user_leaderboard = CatProfile.objects.filter(pk__in=[x.profile_id for x in all_distinct_profile_tags])\
        .annotate(tag_count=Count('tags')).order_by('-tag_count')
    general_user_rank = 0
    for i in range(0, len(general_user_leaderboard)):
        if general_user_leaderboard[i].user_id == profile.user_id:
            general_user_rank = (i + 1)
            break
    content = {
        'error': 0,
        'stats': {
            'decisions': all_tags.count(),
            'users': all_distinct_profile_tags.count(),
            'tagged': all_tags.distinct('photo').count(),
            'rank': general_user_rank
        }
    }
    for a in albums:
        all_album_tags = all_tags.filter(album=a)
        total_tagged_photos_count = all_album_tags.distinct('photo').count()
        user_tags = all_album_tags.filter(profile=profile)
        user_tags_count = user_tags.count()
        user_tagged_photos_count = user_tags.distinct('photo').count()
        user_distinct_album_tags = all_album_tags.distinct('profile')
        total_user_count = user_distinct_album_tags.count()
        contributing_users = CatProfile.objects.filter(pk__in=[x.profile_id for x in user_distinct_album_tags])
        # There was a bug in here, hope this in memory sorting doesn't turn out to be too slow
        for each in contributing_users:
            each.tag_count = all_album_tags.filter(profile=each).count()
        ordered = sorted(contributing_users, key=operator.attrgetter('tag_count'), reverse=True)
        user_rank = 0
        for i in range(0, len(ordered)):
            if ordered[i].user_id == profile.user_id:
                user_rank = (i + 1)
                break

        ret.append({
            'id': a.id,
            'title': a.title,
            'subtitle': a.subtitle,
            'image': request.build_absolute_uri(reverse('project.sift.views.cat_album_thumb', args=(a.id,))) + '?' + str(time.time()),
            'tagged': user_tagged_photos_count,
            'total': a.photos.count(),
            'decisions': user_tags_count,
            'stats': {
                'users': total_user_count,
                'decisions': all_album_tags.count(),
                'tagged': total_tagged_photos_count,
                'rank': user_rank
            }
        })
    content['error'] = error
    content['albums'] = ret

    return Response(content)


def _get_album_state(request, form):
    content = {
        'error': 0,
        'photos': [],
        'state': str(int(round(time.time() * 1000)))
    }
    if form.is_valid():
        all_cat_tags = set(CatTag.objects.filter(active=True).values_list('name', flat=True))
        album = form.cleaned_data['id']
        content['title'] = album.title
        content['subtitle'] = album.subtitle
        content['image'] = request.build_absolute_uri(reverse('project.sift.views.cat_album_thumb', args=(album.id,)))
        user_tags = CatTagPhoto.objects.filter(profile=request.get_user().profile, album=album)\
            .values('photo').annotate(tag_count=Count('profile'))
        tag_count_dict = {}
        for each in user_tags:
            tag_count_dict[each['photo']] = each['tag_count']
        user_favorites = CatUserFavorite.objects.filter(profile=request.get_user().profile, album=album)\
            .values_list('photo_id', flat=True)
        for p in album.photos.all():
            available_cat_tags = all_cat_tags - set(CatTagPhoto.objects.filter(
                profile=request.get_user().profile, album=album, photo=p).values_list('tag__name', flat=True))
            if form.cleaned_data['max'] == 0:
                to_get = len(available_cat_tags)
            elif 'max' not in form.cleaned_data or form.cleaned_data['max'] is None:
                to_get = 2
            else:
                to_get = form.cleaned_data['max']
            content['photos'].append({
                'id': p.id,
                'image': request.build_absolute_uri(reverse('project.sift.views.cat_photo', args=(p.id,))) + '[DIM]/',
                'title': p.title,
                'author': p.author,
                'user_tags': tag_count_dict[p.id] if p.id in tag_count_dict else 0,
                'source': {'name': p.get_source_with_key(), 'url': p.source_url},
                'tag': random.sample(available_cat_tags, min(len(available_cat_tags), to_get)),
                'is_user_favorite': p.id in user_favorites
            })
        content['photos'] = sorted(content['photos'],
                                   key=lambda y: (y['user_tags'], random.randint(0, len(content['photos']))))
        for each in content['photos']:
            del each['user_tags']
    else:
        content['error'] = 2

    return content


def _utcisoformat(dt):
    return dt.astimezone(utc).replace(tzinfo=None).isoformat()[:-3] + 'Z'


def _get_favorite_object_json_form(request, obj):
    return {
        'id': obj.id,
        'album_id': obj.album.id,
        'photo_id': obj.photo.id,
        'title': obj.photo.title,
        'image': request.build_absolute_uri(reverse('project.sift.views.cat_photo', args=(obj.photo.id,))) + '[DIM]/',
        'date': _utcisoformat(obj.created)
    }


def _get_user_data(request, remove_favorite=None, add_favorite=None):
    profile = request.get_user().profile
    user_cat_tags = CatTagPhoto.objects.filter(profile=profile)
    all_distinct_profile_tags = CatTagPhoto.objects.distinct('profile')
    general_user_leaderboard = CatProfile.objects.filter(pk__in=[x.profile_id for x in all_distinct_profile_tags])\
        .annotate(tag_count=Count('tags')).order_by('-tag_count')
    general_user_rank = 0
    for i in range(0, len(general_user_leaderboard)):
        if general_user_leaderboard[i].user_id == profile.user_id:
            general_user_rank = (i + 1)
            break
    albums_dict = dict((o[0], o[1]) for o in CatAlbum.objects.all().values_list('id', 'title'))
    content = {
        'error': 0,
        'tagged': user_cat_tags.count(),
        'pics': user_cat_tags.distinct('photo').count(),
        'rank': general_user_rank,
        'message': None,
        'link': None,
        'meta': {
            'albums': albums_dict
        }
    }
    if remove_favorite or add_favorite:
        if remove_favorite:
            content['favorites-'] = [remove_favorite]
        elif add_favorite:
            content['favorites+'] = [_get_favorite_object_json_form(request, add_favorite)]
    else:
        user_favorites = CatUserFavorite.objects.filter(profile=profile)
        content['favorites'] = []
        for f in user_favorites:
            content['favorites'].append(_get_favorite_object_json_form(request, f))

    return content


@api_view(['POST'])
@parser_classes((FormParser,))
@authentication_classes((SessionAuthentication, CustomAuthentication))
@permission_classes((AnonymousUserPermission, IsAuthenticated))
def cat_album_state(request):
    cat_album_state_form = CatAlbumStateForm(request.data)
    return Response(_get_album_state(request, cat_album_state_form))


def cat_photo(request, photo_id=None, thumb_size=600):
    if not photo_id:
        photo_id = CatPhoto.objects.order_by('?').first().pk
    cache_key = "ajapaik_cat_photo_response_%s_%s_%s" % (SITE_ID, photo_id, thumb_size)
    cached_response = cache.get(cache_key)
    if cached_response:
        return cached_response
    p = get_object_or_404(CatPhoto, id=photo_id)
    thumb_str = str(thumb_size) + 'x' + str(thumb_size)
    im = get_thumbnail(p.image, thumb_str, upscale=False)
    try:
        content = im.read()
    except IOError:
        delete(im)
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
@authentication_classes((SessionAuthentication, CustomAuthentication))
@permission_classes((AnonymousUserPermission, IsAuthenticated))
def cat_tag(request):
    cat_tag_form = CatTagForm(request.data)
    content = {
        'error': 0,
    }
    if cat_tag_form.is_valid():
        tag = CatTagPhoto(
            tag=cat_tag_form.cleaned_data['tag'],
            album=cat_tag_form.cleaned_data['id'],
            photo=cat_tag_form.cleaned_data['photo'],
            profile_id=request.get_user().profile.id,
            source=cat_tag_form.cleaned_data['source'],
            value=cat_tag_form.cleaned_data['value']
        )
        if not tag.source:
            tag.source = 'mob'
        tag.save()
        content['state'] = str(int(round(time.time() * 1000)))
    else:
        content['error'] = 2

    return Response(content)


@api_view(['POST'])
@parser_classes((FormParser,))
@authentication_classes((CustomAuthentication,))
@permission_classes((IsAuthenticated,))
def user_me(request):
    content = _get_user_data(request)

    return Response(content)


@api_view(['POST'])
@parser_classes((FormParser,))
@authentication_classes((SessionAuthentication, CustomAuthentication))
@permission_classes((AnonymousUserPermission, IsAuthenticated))
def user_favorite_add(request):
    cat_favorite_form = CatFavoriteForm(request.data)
    profile = request.get_user().profile
    content = {
        'error': 2
    }
    if cat_favorite_form.is_valid():
        try:
            cat_user_favorite = CatUserFavorite(
                album=cat_favorite_form.cleaned_data['album'],
                photo=cat_favorite_form.cleaned_data['photo'],
                profile_id=profile.id
            )
            cat_user_favorite.save()
            content = _get_user_data(request, add_favorite=cat_user_favorite)
        except IntegrityError:
            content = _get_user_data(request)
            content['error'] = 0

    return Response(content)


@api_view(['POST'])
@parser_classes((FormParser,))
@authentication_classes((SessionAuthentication, CustomAuthentication))
@permission_classes((AnonymousUserPermission, IsAuthenticated))
def user_favorite_remove(request):
    cat_favorite_form = CatFavoriteForm(request.data)
    profile = request.get_user().profile
    content = {
        'error': 2
    }
    if cat_favorite_form.is_valid():
        try:
            cat_user_favorite = CatUserFavorite.objects.get(
                album=cat_favorite_form.cleaned_data['album'],
                photo=cat_favorite_form.cleaned_data['photo'],
                profile_id=profile.id
            )
            user_favorite_id = deepcopy(cat_user_favorite.id)
            cat_user_favorite.delete()
            content = _get_user_data(request, remove_favorite=user_favorite_id)
        except ObjectDoesNotExist:
            content = _get_user_data(request)
            content['error'] = 2

    return Response(content)

icon_map = {
    'interior': 'local_hotel',
    'exterior': 'nature_people',
    'view': 'home',
    'social': 'accessibility',
    'ground': 'nature_people',
    'raised': 'filter_drama',
    'rural': 'nature',
    'urban': 'location_city',
    'nature': 'nature',
    'manmade': 'location_city',
    'one': 'person',
    'many': 'group_add',
    'public': 'public',
    'private': 'vpn_lock',
    'whole': 'landscape',
    'detail': 'local_florist',
    'staged': 'account_box',
    'natural': 'directions_walk'
}

# Extra translations for Django to pick up
_('Interior')
_('Exterior')
_('View')
_('Social')
_('Ground')
_('Raised')
_('Rural')
_('Urban')
_('One')
_('Many')
_('Public')
_('Private')
_('Whole')
_('Detail')
_('Staged')
_('Natural')
_('Manmade')
_('Nature')

@vary_on_headers('X-Requested-With')
def cat_results(request):
    # Ensure user has profile
    request.get_user()
    filter_form = CatResultsFilteringForm(request.GET)
    json_state = {}
    tag_dict = dict(CatTag.objects.filter(active=True).values_list('name', 'id'))
    for key in tag_dict:
        tag_dict[key] = {
            'id': tag_dict[key],
            'left': key.split('_')[0].strip().capitalize(),
            'right': key.split('_')[2].strip().capitalize(),
            'left_icon': icon_map[key.split('_')[0]].strip(),
            'right_icon': icon_map[key.split('_')[2]].strip(),
        }
    json_state['filterNames'] = tag_dict.keys()
    selected_tag_value_dict = {}
    photo_serializer = None
    page = 0
    total_results = 0
    current_result_set_start = 0
    current_result_set_end = 0
    q = ''
    if filter_form.is_valid():
        cd = filter_form.cleaned_data
        if cd['page']:
            page = cd['page']
            if page > 0:
                page -= 1
        if cd['show_pictures'] or cd['album'] or not (cd['show_pictures'] and cd['album']):
            photos = CatPhoto.objects.all()
            if cd['album']:
                json_state['albumId'] = cd['album'].pk
                json_state['albumName'] = cd['album'].title
                photos = photos.filter(album=cd['album'])
            if cd['show_pictures']:
                json_state['showPictures'] = True
            for k in cd:
                if k in tag_dict.keys():
                    if cd[k]:
                        if k not in selected_tag_value_dict:
                            selected_tag_value_dict[k] = {'left': False, 'na': False, 'right': False}
                        if '1' in cd[k]:
                            selected_tag_value_dict[k]['left'] = True
                            photos = photos.filter(catappliedtag__tag__name=tag_dict[k]['left'].lower())
                            print tag_dict[k]['left'].lower()
                        if '0' in cd[k]:
                            selected_tag_value_dict[k]['na'] = True
                            photos = photos.filter(catappliedtag__tag__name=(k + '_NA'))
                        if '-1' in cd[k]:
                            selected_tag_value_dict[k]['right'] = True
                            photos = photos.filter(catappliedtag__tag__name=tag_dict[k]['right'].lower())
            if cd['q']:
                q = cd['q']
                cat_photo_search_form = HaystackCatPhotoSearchForm({'q': q})
                search_query_set = cat_photo_search_form.search()
                results = [r.pk for r in search_query_set]
                photos = photos.filter(pk__in=results)
            photos = photos.distinct()
            total_results = photos.count()
            json_state['totalResults'] = total_results
            photos = photos.annotate(favorited=Count('catuserfavorite')).order_by('-favorited')[page * CAT_RESULTS_PAGE_SIZE: (page + 1) * CAT_RESULTS_PAGE_SIZE]#.prefetch_related('source')
            current_result_set_start = page * CAT_RESULTS_PAGE_SIZE
            current_result_set_end = (page + 1) * CAT_RESULTS_PAGE_SIZE
            if current_result_set_start == 0:
                current_result_set_start = 1
            if current_result_set_end > total_results:
                current_result_set_end = total_results
            json_state['currentResultSetStart'] = current_result_set_start
            json_state['currentResultSetEnd'] = current_result_set_end
            # potential_existing_ajapaik_photos = Photo.objects.filter(source_key__in=(x['source_key'] for x in photos.values('source_key', 'favorited'))).prefetch_related('source')
            # for cp in photos:
            #     cp.in_ajapaik = False
            #     for ap in potential_existing_ajapaik_photos:
            #         if ap.source == cp.source and ap.source_key == cp.source_key:
            #             cp.in_ajapaik = True
            #             break
            photo_serializer = CatResultsPhotoSerializer(photos, many=True)
            json_state['photos'] = photo_serializer.data
    if request.is_ajax():
        if not photo_serializer:
            photos = CatPhoto.objects.all()
            json_state['totalResults'] = photos.count()
            photos = photos.annotate(favorited=Count('catuserfavorite')).order_by('-favorited')[page * CAT_RESULTS_PAGE_SIZE: (page + 1) * CAT_RESULTS_PAGE_SIZE]
            json_state['currentResultSetStart'] = page * CAT_RESULTS_PAGE_SIZE
            json_state['currentResultSetEnd'] = (page + 1) * CAT_RESULTS_PAGE_SIZE
            # potential_existing_ajapaik_photos = Photo.objects.filter(source_key__in=(photos.values_list('source_key', flat=True)))
            # for cp in photos:
            #     cp.in_ajapaik = False
            #     for ap in potential_existing_ajapaik_photos:
            #         if ap.source == cp.source and ap.source_key == cp.source_key:
            #             cp.in_ajapaik = True
            #             break
            photo_serializer = CatResultsPhotoSerializer(photos, many=True)
            json_state['photos'] = photo_serializer.data
        return HttpResponse(JSONRenderer().render(json_state), content_type="application/json")
    else:
        albums = CatAlbum.objects.all()
        json_state['page'] = page + 1
        if 'albumName' in json_state:
            title = json_state['albumName'] + ' - ' + _('Filter photos by tags')
        else:
            title = _('Filter photos by tags')
        return render_to_response('cat_results.html', RequestContext(request, {
            'title': title,
            'is_filter': True,
            'q': q,
            'albums': albums,
            'tag_dict': tag_dict,
            'page': page + 1,
            'current_result_set_start': current_result_set_start,
            'current_result_set_end': current_result_set_end,
            'total_results': total_results,
            'selected_tag_value_dict': selected_tag_value_dict,
            'state_json': dumps(json_state)
        }))



def cat_about(request):
    # Ensure user has profile
    request.get_user()
    return render_to_response('cat_about.html', RequestContext(request, {
        'title': _('About'),
        'is_about': True
    }))


def cat_tagger(request):
    # Ensure user has profile
    request.get_user()
    state = {}
    album_selection_form = CatTaggerAlbumSelectionForm(request.GET)
    title = _('Tag historic photos')
    if album_selection_form.is_valid():
        state['albumId'] = album_selection_form.cleaned_data['album'].pk
        state['albumName'] = album_selection_form.cleaned_data['album'].title
        title = state['albumName'] + ' - ' + _('Tag historic photos')
    request.get_user()
    all_tags = CatTag.objects.filter(active=True)
    state['allTags'] = { x.name: {'leftIcon': icon_map[x.name.split('_')[0]], 'rightIcon': icon_map[x.name.split('_')[-1]]} for x in all_tags }
    albums = CatAlbum.objects.all()
    return render_to_response('cat_tagger.html', RequestContext(request, {
        'title': title,
        'is_tag': True,
        'albums': albums,
        'state_json': dumps(state)
    }))


@api_view(['POST'])
@parser_classes((FormParser,))
@authentication_classes((CustomAuthentication,))
@permission_classes((IsAuthenticated,))
def cat_register_push(request):
    cat_push_register_form = CatPushRegisterForm(request.data)
    profile = request.get_user().profile
    cat_push_register_form.data["profile"] = profile
    content = {
        'error': 4
    }
    if cat_push_register_form.is_valid():
        try:
            existing_device = CatPushDevice.objects.get(
                type=cat_push_register_form.cleaned_data['type'],
                profile_id=profile.id
            )
            existing_device.push_token = cat_push_register_form.cleaned_data['token']
            existing_device.save()
            content['error'] = 0
        except ObjectDoesNotExist:
            cat_push_register_form.save()
            content['error'] = 0
    else:
        content['error'] = 2

    return Response(content)


@api_view(['POST'])
@parser_classes((FormParser,))
@authentication_classes((CustomAuthentication,))
@permission_classes((IsAuthenticated,))
def cat_deregister_push(request):
    cat_push_register_form = CatPushRegisterForm(request.data)
    profile = request.get_user().profile
    content = {
        'error': 0
    }
    cat_push_register_form.data["profile"] = profile
    if cat_push_register_form.is_valid():
        try:
            CatPushDevice.objects.get(
                type=cat_push_register_form.cleaned_data['type'],
                token=cat_push_register_form.cleaned_data['token'],
                profile_id=profile.id
            ).delete()
        except ObjectDoesNotExist:
            content['error'] = 4
    else:
        content['error'] = 2

    return Response(content)


def logout(request):
    from django.contrib.auth import logout

    logout(request)

    if "HTTP_REFERER" in request.META:
        return redirect(request.META["HTTP_REFERER"])

    return redirect("/")