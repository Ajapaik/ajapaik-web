# encoding: utf-8
import datetime
import json as json
import operator
import shutil
import unicodedata
import urllib2
from StringIO import StringIO
from copy import deepcopy
from math import ceil
from time import strftime, strptime

import cv2
import django_comments
import requests
from PIL import Image, ImageFile, ImageOps
from PIL.ExifTags import TAGS, GPSTAGS
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile
from django.core.urlresolvers import reverse
from django.db.models import Sum, Q, Count
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt, csrf_protect
from django_comments.models import CommentFlag
from django_comments.signals import comment_was_flagged
from django_comments.views.utils import next_redirect
from rest_framework.renderers import JSONRenderer
from sorl.thumbnail import delete
from sorl.thumbnail import get_thumbnail

from project.ajapaik.curator_drivers.common import CuratorSearchForm
from project.ajapaik.curator_drivers.finna import FinnaDriver
from project.ajapaik.curator_drivers.flickr_commons import FlickrCommonsDriver
from project.ajapaik.curator_drivers.valimimoodul import ValimimoodulDriver
from project.ajapaik.forms import AddAlbumForm, AreaSelectionForm, AlbumSelectionForm, AddAreaForm, \
    CuratorPhotoUploadForm, GameAlbumSelectionForm, CuratorAlbumEditForm, SubmitGeotagForm, \
    GameNextPhotoForm, GamePhotoSelectionForm, MapDataRequestForm, GalleryFilteringForm, PhotoSelectionForm, \
    SelectionUploadForm, ConfirmGeotagForm, HaystackPhotoSearchForm, AlbumInfoModalForm, PhotoLikeForm, \
    AlbumSelectionFilteringForm, HaystackAlbumSearchForm, DatingSubmitForm, DatingConfirmForm, VideoStillCaptureForm, \
    PhotoUploadChoiceForm, UserPhotoUploadForm, UserPhotoUploadAddAlbumForm, CuratorWholeSetAlbumsSelectionForm
from project.ajapaik.models import Photo, Profile, Source, Device, DifficultyFeedback, GeoTag, Points, \
    Album, AlbumPhoto, Area, Licence, Skip, _calc_trustworthiness, _get_pseudo_slug_for_photo, PhotoLike, \
    Newsletter, Dating, DatingConfirmation, Video
from project.ajapaik.serializers import CuratorAlbumSelectionAlbumSerializer, CuratorMyAlbumListAlbumSerializer, \
    CuratorAlbumInfoSerializer, FrontpageAlbumSerializer, DatingSerializer, VideoSerializer
from project.ajapaik.settings import DATING_POINTS, DATING_CONFIRMATION_POINTS, \
    CURATOR_FLICKR_ENABLED, CURATOR_THEN_AND_NOW_CREATION_DISABLED
from project.ajapaik.then_and_now_tours import user_has_confirmed_email
from project.utils import calculate_thumbnail_size, convert_to_degrees, calculate_thumbnail_size_max_height, \
    distance_in_meters, angle_diff

ImageFile.LOAD_TRUNCATED_IMAGES = True


@cache_control(max_age=604800)
def image_thumb(request, photo_id=None, thumb_size=250, pseudo_slug=None):
    thumb_size = int(thumb_size)
    if 0 < thumb_size <= 400:
        thumb_size = 400
    else:
        thumb_size = 1024
    p = get_object_or_404(Photo, id=photo_id)
    thumb_str = str(thumb_size) + 'x' + str(thumb_size)
    if p.rephoto_of:
        original_thumb = get_thumbnail(p.rephoto_of.image, thumb_str, upscale=False)
        thumb_str = str(original_thumb.size[0]) + 'x' + str(original_thumb.size[1])
        im = get_thumbnail(p.image, thumb_str, upscale=True, downscale=True, crop='center')
    else:
        im = get_thumbnail(p.image, thumb_str, upscale=False)
    try:
        content = im.read()
    except IOError:
        delete(im)
        im = get_thumbnail(p.image, thumb_str, upscale=False)
        content = im.read()

    return HttpResponse(content, content_type='image/jpg')


@cache_control(max_age=604800)
def image_full(request, photo_id=None, pseudo_slug=None):
    p = get_object_or_404(Photo, id=photo_id)
    content = p.image.read()

    return HttpResponse(content, content_type='image/jpg')


def get_general_info_modal_content(request):
    profile = request.get_user().profile
    photo_qs = Photo.objects.filter(rephoto_of__isnull=True)
    rephoto_qs = Photo.objects.filter(rephoto_of__isnull=False)
    user_rephoto_qs = rephoto_qs.filter(user=profile)
    geotags_qs = GeoTag.objects.filter()
    ret = {
        "total_photo_count": photo_qs.count(),
        "contributing_users": geotags_qs.distinct('user').count(),
        "total_photos_tagged": photo_qs.filter(lat__isnull=False, lon__isnull=False).count(),
        "rephoto_count": rephoto_qs.count(),
        "rephotographing_users": rephoto_qs.order_by('user').distinct('user').count(),
        "rephotographed_photo_count": rephoto_qs.order_by('rephoto_of_id').distinct('rephoto_of_id').count(),
        "user_geotagged_photos": geotags_qs.filter(user=profile).distinct('photo').count(),
        "user_rephotos": user_rephoto_qs.count(),
        "user_rephotographed_photos": user_rephoto_qs.order_by(
            'rephoto_of_id').distinct('rephoto_of_id').count()
    }

    return render_to_response("_general_info_modal_content.html", RequestContext(request, ret))


def get_album_info_modal_content(request):
    profile = request.get_user().profile
    form = AlbumInfoModalForm(request.GET)
    if form.is_valid():
        album = form.cleaned_data['album']
        ret = {'album': album, 'link_to_map': form.cleaned_data['linkToMap'],
               'link_to_game': form.cleaned_data['linkToGame'], 'link_to_gallery': form.cleaned_data['linkToGallery'],
               'fb_share_game': form.cleaned_data['fbShareGame'], 'fb_share_map': form.cleaned_data['fbShareMap'],
               'fb_share_gallery': form.cleaned_data['fbShareGallery'],
               'total_photo_count': album.photo_count_with_subalbums,
               'geotagged_photo_count': album.geotagged_photo_count_with_subalbums}

        album_photo_ids = album.get_all_photos_queryset_with_subalbums().values_list('id', flat=True)
        geotags_for_album_photos = GeoTag.objects.filter(photo_id__in=album_photo_ids)
        ret['user_geotagged_photo_count'] = geotags_for_album_photos.filter(user=profile).distinct('photo_id').count()
        ret['geotagging_user_count'] = geotags_for_album_photos.distinct('user').count()

        ret['rephoto_count'] = album.rephoto_count_with_subalbums
        rephotos_qs = album.get_rephotos_queryset_with_subalbums()
        ret['rephoto_user_count'] = rephotos_qs.order_by('user_id').distinct('user_id').count()
        ret['rephotographed_photo_count'] = rephotos_qs.order_by('rephoto_of_id').distinct('rephoto_of_id').count()

        album_user_rephotos = rephotos_qs.filter(user=profile)
        ret['user_rephoto_count'] = album_user_rephotos.count()
        ret['user_rephotographed_photo_count'] = album_user_rephotos.order_by('rephoto_of_id').distinct(
            'rephoto_of_id').count()
        if ret['rephoto_user_count'] == 1 and ret['user_rephoto_count'] == ret['rephoto_count']:
            ret['user_made_all_rephotos'] = True
        else:
            ret['user_made_all_rephotos'] = False

        # Get all users that have either curated into selected photo set or re-curated into selected album
        album_photo_ids = album_photo_ids
        users_curated_into_this_or_sub = AlbumPhoto.objects.filter(photo_id__in=album_photo_ids, profile__isnull=False,
                                                                   type=AlbumPhoto.CURATED, album=album).values(
            'profile').annotate(count=Count('profile'))
        users_recurated_into_this = AlbumPhoto.objects.filter(album=album, type=AlbumPhoto.RECURATED,
                                                              profile__isnull=False).values('profile').annotate(
            count=Count('profile'))
        final_score_dict = {}
        for u in users_curated_into_this_or_sub:
            final_score_dict[u['profile']] = u['count']
        for u in users_recurated_into_this:
            if u['profile'] in final_score_dict:
                final_score_dict[u['profile']] += u['count']
            else:
                final_score_dict[u['profile']] = u['count']
        album_curators = Profile.objects.filter(user_id__in=final_score_dict.keys(), first_name__isnull=False,
                                                last_name__isnull=False)
        final_score_dict = [x[0] for x in sorted(final_score_dict.items(), key=operator.itemgetter(1), reverse=True)]
        album_curators = list(album_curators)
        album_curators.sort(key=lambda z: final_score_dict.index(z.id))
        ret['album_curators'] = album_curators

        if album.lat and album.lon:
            ret['nearby_albums'] = Album.objects.filter(geography__distance_lte=(
                Point(album.lon, album.lat), D(m=50000)), is_public=True, atype=Album.CURATED).exclude(
                id=album.id).order_by('?')[:3]
        album_id_str = str(album.id)
        ret['share_game_link'] = request.build_absolute_uri(
            reverse('project.ajapaik.views.game')) + '?album=' + album_id_str
        ret['share_map_link'] = request.build_absolute_uri(
            reverse('project.ajapaik.views.mapview')) + '?album=' + album_id_str
        ret['share_gallery_link'] = request.build_absolute_uri(
            reverse('project.ajapaik.views.frontpage')) + '?album=' + album_id_str

        return render_to_response('_info_modal_content.html', RequestContext(request, ret))

    return HttpResponse('Error')


def _get_exif_data(img):
    try:
        exif = img._getexif()
    except (AttributeError, IOError, KeyError, IndexError):
        exif = None
    if exif is None:
        return None
    exif_data = {}
    for (tag, value) in exif.items():
        decoded = TAGS.get(tag, tag)
        if decoded == "GPSInfo":
            for t in value:
                sub_decoded = GPSTAGS.get(t, t)
                exif_data[str(decoded) + "." + str(sub_decoded)] = value[t]
        elif len(str(value)) < 50:
            exif_data[decoded] = value
        else:
            exif_data[decoded] = None

    return exif_data


def _extract_and_save_data_from_exif(photo_with_exif):
    img = Image.open(settings.MEDIA_ROOT + "/" + str(photo_with_exif.image))
    exif_data = _get_exif_data(img)
    if exif_data:
        if "GPSInfo.GPSLatitudeRef" in exif_data and "GPSInfo.GPSLatitude" in exif_data and "GPSInfo.GPSLongitudeRef" \
                in exif_data and "GPSInfo.GPSLongitude" in exif_data:
            gps_latitude_ref = exif_data.get("GPSInfo.GPSLatitudeRef")
            gps_latitude = exif_data.get("GPSInfo.GPSLatitude")
            gps_longitude_ref = exif_data.get("GPSInfo.GPSLongitudeRef")
            gps_longitude = exif_data.get("GPSInfo.GPSLongitude")
            lat = convert_to_degrees(gps_latitude)
            if gps_latitude_ref != "N":
                lat = 0 - lat
            lon = convert_to_degrees(gps_longitude)
            if gps_longitude_ref != "E":
                lon = 0 - lon
            photo_with_exif.lat = lat
            photo_with_exif.lon = lon
            photo_with_exif.save()
        if "Make" in exif_data or "Model" in exif_data or "LensMake" in exif_data or "LensModel" in exif_data \
                or "Software" in exif_data:
            camera_make = exif_data.get("Make")
            camera_model = exif_data.get("Model")
            lens_make = exif_data.get("LensMake")
            lens_model = exif_data.get("LensModel")
            software = exif_data.get("Software")
            try:
                device = Device.objects.get(camera_make=camera_make, camera_model=camera_model, lens_make=lens_make,
                                            lens_model=lens_model, software=software)
            except ObjectDoesNotExist:
                try:
                    device = Device(camera_make=camera_make, camera_model=camera_model, lens_make=lens_make,
                                    lens_model=lens_model, software=software)
                    device.save()
                except:
                    device = None
            photo_with_exif.device = device
            photo_with_exif.save()
        if "DateTimeOriginal" in exif_data and not photo_with_exif.date:
            date_taken = exif_data.get("DateTimeOriginal")
            try:
                parsed_time = strptime(date_taken, "%Y:%m:%d %H:%M:%S")
            except ValueError:
                parsed_time = None
            if parsed_time:
                parsed_time = strftime("%H:%M:%S", parsed_time)
            # ignore default camera dates
            if parsed_time and parsed_time != "12:00:00" and parsed_time != "00:00:00":
                try:
                    parsed_date = strptime(date_taken, "%Y:%m:%d %H:%M:%S")
                except ValueError:
                    parsed_date = None
                if parsed_date:
                    photo_with_exif.date = strftime("%Y-%m-%d", parsed_date)
                    photo_with_exif.save()
        return True
    else:
        return False


def _get_album_choices(qs=None, start=None, end=None):
    if qs:
        albums = qs.prefetch_related("cover_photo").order_by("-created")[start:end]
    else:
        albums = Album.objects.filter(is_public=True).prefetch_related("cover_photo").order_by("-created")[start:end]
    for a in albums:
        if a.cover_photo:
            a.cover_photo_width, a.cover_photo_height = calculate_thumbnail_size(a.cover_photo.width,
                                                                                 a.cover_photo.height, 400)
        else:
            a.cover_photo_width, a.cover_photo_height = 400, 300

    return albums


def _calculate_recent_activity_scores():
    c = min(5000, Points.objects.all().count())
    recent_actions = []
    try:
        five_thousand_actions_ago = Points.objects.order_by('-created')[c - 1].created
        recent_actions = Points.objects.filter(created__gt=five_thousand_actions_ago).values('user_id') \
            .annotate(total_points=Sum('points'))
    except IndexError:
        pass
    recent_action_dict = {}
    for each in recent_actions:
        recent_action_dict[each['user_id']] = each['total_points']
    recent_actors = Profile.objects.filter(pk__in=recent_action_dict.keys())
    for each in recent_actors:
        each.score_recent_activity = recent_action_dict[each.pk]
        each.save()
    # Profile.objects.bulk_update(recent_actors, update_fields=['score_recent_activity'])
    # Check for people who somehow no longer have actions among the last 5000
    orphan_profiles = Profile.objects.filter(score_recent_activity__gt=0).exclude(pk__in=[x.pk for x in recent_actors])
    orphan_profiles.update(score_recent_activity=0)


def _get_leaderboard(profile):
    # General small leaderboard doesn't have anonymous users, displays recent activity score
    # TODO: Should also show first place, where did that code go?
    profile_rank = Profile.objects.filter(score_recent_activity__gt=profile.score_recent_activity,
                                          first_name__isnull=False, last_name__isnull=False).count() + 1
    leaderboard_queryset = Profile.objects.filter(
        Q(first_name__isnull=False, last_name__isnull=False, score_recent_activity__gt=0) |
        Q(pk=profile.id)).order_by('-score_recent_activity')
    start = profile_rank - 2
    if start < 0:
        start = 0
    nearby_users = leaderboard_queryset[start:profile_rank + 1]
    n = start + 1
    for each in nearby_users:
        if each == profile:
            each.is_current_user = True
        each.position = n
        n += 1

    return nearby_users


# TODO: Leaderboards should be generated by cron jobs, I'm guessing the 'Tallinn' album leaderboard takes minutes to load by now
def _get_album_leaderboard50(profile_id, album_id=None):
    album = Album.objects.get(pk=album_id)
    album_photos_qs = album.get_historic_photos_queryset_with_subalbums()
    album_photo_ids = frozenset(album_photos_qs.values_list('id', flat=True))
    album_photos_with_rephotos = album_photos_qs.filter(rephotos__isnull=False).prefetch_related('rephotos')
    album_rephoto_ids = []
    for each in album_photos_with_rephotos:
        for rp in each.rephotos.all():
            album_rephoto_ids.append(rp.id)
    photo_points = Points.objects.prefetch_related('user') \
        .filter(photo_id__in=album_photo_ids, points__gt=0)
    photo_points = photo_points | Points.objects.prefetch_related('user') \
        .filter(photo_id__in=album_rephoto_ids, points__gt=0).exclude(action=Points.PHOTO_RECURATION)
    photo_points = photo_points | Points.objects.filter(photo_id__in=album_photo_ids, album=album,
                                                        action=Points.PHOTO_RECURATION).prefetch_related('user')
    # TODO: This should not be done in Python memory, but with a query
    user_score_map = {}
    for each in photo_points:
        if each.user_id in user_score_map:
            user_score_map[each.user_id] += each.points
        else:
            user_score_map[each.user_id] = each.points
    if profile_id not in user_score_map:
        user_score_map[profile_id] = 0
    sorted_scores = sorted(user_score_map.items(), key=operator.itemgetter(1), reverse=True)[:50]
    pk_list = [x[0] for x in sorted_scores]
    try:
        current_user_rank = pk_list.index(profile_id)
    except ValueError:
        current_user_rank = len(sorted_scores)
    current_user_rank += 1
    # Works on Postgres, we don't really need to worry about this I guess...maybe only if it gets slow
    clauses = ' '.join(['WHEN user_id=%s THEN %s' % (pk, i) for i, pk in enumerate(pk_list)])
    ordering = 'CASE %s END' % clauses
    top_users = Profile.objects.filter(Q(user_id__in=pk_list) | Q(user_id=profile_id)) \
        .extra(select={'ordering': ordering}, order_by=('ordering',)).prefetch_related('user')
    n = 1
    for each in top_users:
        if each.user_id == profile_id:
            each.is_current_user = True
        each.custom_score = user_score_map[each.user_id]
        each.position = n
        n += 1

    return top_users, album.name


def _get_all_time_leaderboard50(profile_id):
    lb = Profile.objects.filter(
        Q(first_name__isnull=False, last_name__isnull=False) |
        Q(pk=profile_id)).order_by('-score').prefetch_related('user')[:50]
    n = 1
    for each in lb:
        if each.user_id == profile_id:
            each.is_current_user = True
        each.position = n
        n += 1

    return lb


@csrf_exempt
def rephoto_upload(request, photo_id):
    photo = get_object_or_404(Photo, pk=photo_id)
    new_id = 0
    if request.method == 'POST':
        profile = request.get_user().profile
        user = request.get_user()
        # FIXME: Our interfaces block non-authenticated uploading, but clearly it's possible
        if 'fb_access_token' in request.POST:
            token = request.POST.get('fb_access_token')
            profile, fb_data = Profile.facebook.get_user(token)
            if profile is None:
                user = request.get_user()
                profile = user.profile
                profile.update_from_fb_data(token, fb_data)
        if not profile.fb_id and not profile.google_plus_id and not user.email:
            return HttpResponse(json.dumps({'error': _('Non-authenticated user')}), content_type='application/json')
        if 'user_file[]' in request.FILES.keys():
            for f in request.FILES.getlist('user_file[]'):
                file_obj = ContentFile(f.read())
                data = request.POST
                date_taken = data.get('dateTaken', None)
                re_photo = Photo(
                    rephoto_of=photo,
                    area=photo.area,
                    licence=Licence.objects.get(url='https://creativecommons.org/licenses/by-sa/4.0/'),
                    description=data.get('description', photo.description),
                    lat=data.get('lat', None),
                    lon=data.get('lon', None),
                    date_text=data.get('date_text', None),
                    user=profile,
                    cam_scale_factor=data.get('scale_factor', None),
                    cam_yaw=data.get('yaw'),
                    cam_pitch=data.get('pitch'),
                    cam_roll=data.get('roll'),
                )
                if date_taken is not None:
                    try:
                        parsed_date_taken = strptime(date_taken, '%d.%m.%Y %H:%M')
                        re_photo.date = strftime('%Y-%m-%d %H:%M', parsed_date_taken)
                    except:
                        pass
                else:
                    re_photo.date = datetime.datetime.now()
                if re_photo.cam_scale_factor:
                    re_photo.cam_scale_factor = round(float(re_photo.cam_scale_factor), 6)
                re_photo.save()
                photo.save()
                for each in photo.albums.all():
                    each.rephoto_count_with_subalbums = each.get_rephotos_queryset_with_subalbums().count()
                    each.light_save()
                re_photo.image.save('rephoto.jpg', file_obj)
                new_id = re_photo.pk
                img = Image.open(settings.MEDIA_ROOT + '/' + str(re_photo.image))
                _extract_and_save_data_from_exif(re_photo)

                if re_photo.cam_scale_factor:
                    new_size = tuple([int(x * re_photo.cam_scale_factor) for x in img.size])
                    output_file = StringIO()
                    if re_photo.cam_scale_factor < 1:
                        x0 = (img.size[0] - new_size[0]) / 2
                        y0 = (img.size[1] - new_size[1]) / 2
                        x1 = img.size[0] - x0
                        y1 = img.size[1] - y0
                        new_img = img.transform(new_size, Image.EXTENT, (x0, y0, x1, y1))
                        new_img.save(output_file, 'JPEG', quality=95)
                        re_photo.image_unscaled = deepcopy(re_photo.image)
                        re_photo.image.save(str(re_photo.image), ContentFile(output_file.getvalue()))
                    elif re_photo.cam_scale_factor > 1:
                        x0 = (new_size[0] - img.size[0]) / 2
                        y0 = (new_size[1] - img.size[1]) / 2
                        new_img = Image.new('RGB', new_size)
                        new_img.paste(img, (x0, y0))
                        new_img.save(output_file, 'JPEG', quality=95)
                        re_photo.image_unscaled = deepcopy(re_photo.image)
                        re_photo.image.save(str(re_photo.image), ContentFile(output_file.getvalue()))

        profile.update_rephoto_score()
        profile.set_calculated_fields()
        profile.save()

    return HttpResponse(json.dumps({'new_id': new_id}), content_type='application/json')


def logout(request):
    from django.contrib.auth import logout

    logout(request)

    if "HTTP_REFERER" in request.META:
        return redirect(request.META["HTTP_REFERER"])

    return redirect("/")


@ensure_csrf_cookie
def game(request):
    profile = request.get_user().profile
    user_has_likes = profile.likes.count() > 0
    user_has_rephotos = profile.photos.filter(rephoto_of__isnull=False).count() > 0
    area_selection_form = AreaSelectionForm(request.GET)
    album_selection_form = AlbumSelectionForm(request.GET)
    game_album_selection_form = GameAlbumSelectionForm(request.GET)
    game_photo_selection_form = GamePhotoSelectionForm(request.GET)
    album = None
    area = None
    ret = {
        "albums": _get_album_choices()
    }

    if game_photo_selection_form.is_valid():
        p = game_photo_selection_form.cleaned_data["photo"]
        ret["photo"] = p
        album_ids = AlbumPhoto.objects.filter(photo_id=p.id).distinct("album_id").values_list("album_id", flat=True)
        album = Album.objects.filter(id__in=album_ids, atype=Album.CURATED).order_by('-created').first()
    elif game_album_selection_form.is_valid():
        album = game_album_selection_form.cleaned_data["album"]
    else:
        if area_selection_form.is_valid():
            area = area_selection_form.cleaned_data["area"]
        else:
            old_city_id = request.GET.get("city__pk") or None
            if old_city_id is not None:
                area = Area.objects.get(pk=old_city_id)
        ret["area"] = area

    facebook_share_photos = None
    if album:
        ret["album"] = (album.id, album.name, album.lat, album.lon, ','.join(album.name.split(' ')))
        qs = album.photos.filter(rephoto_of__isnull=True)
        for sa in album.subalbums.exclude(atype=Album.AUTO):
            qs = qs | sa.photos.filter(rephoto_of__isnull=True)
        ret["album_photo_count"] = qs.distinct('id').count()
        facebook_share_photos = album.photos.all()
    elif area:
        facebook_share_photos = Photo.objects.filter(area=area, rephoto_of__isnull=True).order_by("?")

    ret["facebook_share_photos"] = []
    if facebook_share_photos:
        for each in facebook_share_photos[:5]:
            ret["facebook_share_photos"].append([each.pk, each.get_pseudo_slug(), each.width, each.height])

    site = Site.objects.get_current()
    ret["hostname"] = "https://%s" % (site.domain,)
    if album:
        ret["title"] = album.name
    elif area:
        ret["title"] = area.name
    else:
        ret["title"] = _("Geotagging game")
    ret["is_game"] = True
    ret["area_selection_form"] = area_selection_form
    ret["album_selection_form"] = album_selection_form
    ret["last_geotagged_photo_id"] = Photo.objects.order_by('-latest_geotag').first().id
    ret["ajapaik_facebook_link"] = settings.AJAPAIK_FACEBOOK_LINK
    ret["user_has_likes"] = user_has_likes
    ret["user_has_rephotos"] = user_has_rephotos

    return render_to_response("game.html", RequestContext(request, ret))


def fetch_stream(request):
    profile = request.get_user().profile
    form = GameNextPhotoForm(request.GET)
    data = {"photo": None, "userSeenAll": False, "nothingMoreToShow": False}
    if form.is_valid():
        qs = Photo.objects.filter(rephoto_of__isnull=True)
        form_area = form.cleaned_data["area"]
        form_album = form.cleaned_data["album"]
        form_photo = form.cleaned_data["photo"]
        # TODO: Correct implementation
        if form_photo:
            form_photo.user_already_confirmed = False
            last_confirm_geotag_by_this_user_for_photo = form_photo.geotags.filter(user_id=profile.id,
                                                                                   type=GeoTag.CONFIRMATION).order_by(
                '-created').first()
            if last_confirm_geotag_by_this_user_for_photo and (
                            form_photo.lat == last_confirm_geotag_by_this_user_for_photo.lat
                    and form_photo.lon == last_confirm_geotag_by_this_user_for_photo.lon):
                form_photo.user_already_confirmed = True
            form_photo.user_already_geotagged = form_photo.geotags.filter(user_id=profile.id).exists()
            form_photo.user_likes = PhotoLike.objects.filter(profile=profile, photo=form_photo, level=1).exists()
            form_photo.user_loves = PhotoLike.objects.filter(profile=profile, photo=form_photo, level=2).exists()
            form_photo.user_like_count = PhotoLike.objects.filter(photo=form_photo).distinct('profile').count()
            data = {"photo": Photo.get_game_json_format_photo(form_photo), "userSeenAll": False,
                    "nothingMoreToShow": False}
        else:
            if form_album:
                # TODO: Could be done later where we're frying our brains with nextPhoto logic anyway
                photos_ids_in_album = list(form_album.photos.values_list("id", flat=True))
                subalbums = form_album.subalbums.exclude(atype=Album.AUTO)
                for sa in subalbums:
                    photos_ids_in_subalbum = list(sa.photos.values_list("id", flat=True))
                    photos_ids_in_album += photos_ids_in_subalbum
                qs = qs.filter(pk__in=photos_ids_in_album)
            elif form_area:
                qs = qs.filter(area=form_area)
            # FIXME: Ugly
            try:
                response = Photo.get_next_photo_to_geotag(qs, request)
                data = {"photo": response[0], "userSeenAll": response[1], "nothingMoreToShow": response[2]}
            except IndexError:
                pass

    return HttpResponse(json.dumps(data), content_type="application/json")


# Params for old URL support
def frontpage(request, album_id=None, page=None):
    profile = request.get_user().profile
    data = _get_filtered_data_for_frontpage(request, album_id, page)
    site = Site.objects.get_current()

    user_has_likes = profile.likes.count() > 0
    user_has_rephotos = profile.photos.filter(rephoto_of__isnull=False).count() > 0

    if data['rephotos_by_name']:
        title = _('%(name)s - rephotos') % {'name': data['rephotos_by_name']}
    elif data['album']:
        title = data['album'][1]
    else:
        title = _('Timepatch (Ajapaik)')

    return render_to_response('frontpage.html', RequestContext(request, {
        'is_frontpage': True,
        'title': title,
        'hostname': 'https://%s' % (site.domain,),
        'ajapaik_facebook_link': settings.AJAPAIK_FACEBOOK_LINK,
        'facebook_share_photos': data['fb_share_photos'],
        'album': data['album'],
        # 'albums': albums,
        'photo': data['photo'],
        # 'start': data['start'],
        # 'end': data['end'],
        'page': data['page'],
        'order1': data['order1'],
        'order2': data['order2'],
        'order3': data['order3'],
        'user_has_likes': user_has_likes,
        'user_has_rephotos': user_has_rephotos,
        'my_likes_only': data['my_likes_only'],
        'rephotos_by': data['rephotos_by'],
        'rephotos_by_name': data['rephotos_by_name'],
        'photos_with_comments': data['photos_with_comments'],
        'photos_with_rephotos': data['photos_with_rephotos'],
        'show_photos': data['show_photos'],
        # 'max_page': data['max_page'],
        # 'total': data['total'],
        # 'photos': data['photos'],
        'is_photoset': data['is_photoset'],
        'last_geotagged_photo_id': Photo.objects.order_by('-latest_geotag').first().id
    }))


def frontpage_async_data(request):
    data = _get_filtered_data_for_frontpage(request)
    data['fb_share_photos'] = None

    return HttpResponse(json.dumps(data), content_type="application/json")


def frontpage_async_albums(request):
    form = AlbumSelectionFilteringForm(request.GET)
    ret = {}
    if form.is_valid():
        page = form.cleaned_data['page']
        if page is None:
            page = 1
        page_size = settings.FRONTPAGE_DEFAULT_ALBUM_PAGE_SIZE
        start = (page - 1) * page_size
        albums = Album.objects.filter(is_public=True, cover_photo__isnull=False)
        q = form.cleaned_data['q']
        if q:
            album_search_form = HaystackAlbumSearchForm({'q': q})
            search_query_set = album_search_form.search()
            results = [r.pk for r in search_query_set]
            albums = albums.filter(pk__in=results)
        total = albums.count()
        if start < 0:
            start = 0
        if start > total:
            start = total
        if int(start + page_size) > total:
            end = total
        else:
            end = start + page_size
        end = int(end)
        max_page = int(ceil(float(total) / float(page_size)))

        albums = _get_album_choices(albums, start, end)
        serializer = FrontpageAlbumSerializer(albums, many=True)
        ret['start'] = start
        ret['end'] = end
        ret['total'] = total
        ret['max_page'] = max_page
        ret['page'] = page
        ret['albums'] = JSONRenderer().render(serializer.data)

    return HttpResponse(json.dumps(ret), content_type="application/json")


def _get_filtered_data_for_frontpage(request, album_id=None, page_override=None):
    profile = request.get_user().profile
    photos = Photo.geo.filter(rephoto_of__isnull=True).annotate(rephoto_count=Count('rephotos', distinct=True))
    filter_form = GalleryFilteringForm(request.GET)
    page_size = settings.FRONTPAGE_DEFAULT_PAGE_SIZE
    ret = {}
    if filter_form.is_valid():
        if album_id:
            album = Album.objects.get(pk=album_id)
        else:
            album = filter_form.cleaned_data['album']
        requested_photo = filter_form.cleaned_data['photo']
        requested_photos = filter_form.cleaned_data['photos']
        order1 = filter_form.cleaned_data['order1']
        order2 = filter_form.cleaned_data['order2']
        order3 = filter_form.cleaned_data['order3']
        my_likes_only = filter_form.cleaned_data['myLikes']
        rephotos_by = None
        rephotos_by_name = None
        if filter_form.cleaned_data['rephotosBy']:
            rephotos_by = filter_form.cleaned_data['rephotosBy']
            name = rephotos_by.get_display_name()
            rephotos_by = rephotos_by.pk
            rephotos_by_name = name
        default_ordering = False
        if not order1 and not order2:
            order1 = 'time'
            order2 = 'added'
            default_ordering = True
        lat = filter_form.cleaned_data['lat']
        lon = filter_form.cleaned_data['lon']
        if album or requested_photos or requested_photo or my_likes_only or rephotos_by \
                or filter_form.cleaned_data['order1']:
            show_photos = True
        else:
            show_photos = False
        if page_override:
            page = int(page_override)
        else:
            page = filter_form.cleaned_data['page']
        if album:
            album_photos_qs = album.photos.all()
            for sa in album.subalbums.exclude(atype=Album.AUTO):
                album_photos_qs = album_photos_qs | sa.photos.all()
            album_photo_ids = set(album_photos_qs.values_list('id', flat=True))
            photos = photos.filter(id__in=album_photo_ids)
        if requested_photos:
            requested_photos = requested_photos.split(',')
            ret['is_photoset'] = True
            photos = photos.filter(id__in=requested_photos)
        else:
            ret['is_photoset'] = False
        if my_likes_only:
            photos = photos.filter(likes__profile=profile)
        if rephotos_by:
            rephotos_profile = Profile.objects.filter(pk=rephotos_by).first()
            if rephotos_profile:
                photos = photos.filter(rephotos__user=rephotos_profile)
        photos_with_comments = None
        photos_with_rephotos = None
        q = filter_form.cleaned_data['q']
        if q and show_photos:
            photo_search_form = HaystackPhotoSearchForm({'q': q})
            search_query_set = photo_search_form.search()
            results = [r.pk for r in search_query_set]
            photos = photos.filter(pk__in=results)
        if order1 == 'closest' and lat and lon:
            ref_location = Point(x=lon, y=lat, srid=4326)
            if order3 == 'reverse':
                photos = photos.distance(ref_location).order_by('-distance')
            else:
                photos = photos.distance(ref_location).order_by('distance')
        elif order1 == 'amount':
            if order2 == 'comments':
                if order3 == 'reverse':
                    photos = photos.order_by('comment_count')
                else:
                    photos = photos.order_by('-comment_count')
                photos_with_comments = photos.filter(comment_count__gt=0).count()
            elif order2 == 'rephotos':
                if order3 == 'reverse':
                    photos = photos.order_by('rephoto_count')
                else:
                    photos = photos.order_by('-rephoto_count')
                photos_with_rephotos = photos.filter(rephoto_count__gt=0).count()
            elif order2 == 'geotags':
                if order3 == 'reverse':
                    photos = photos.order_by('geotag_count')
                else:
                    photos = photos.order_by('-geotag_count')
            elif order2 == 'likes':
                if order3 == 'reverse':
                    photos = photos.order_by('like_count')
                else:
                    photos = photos.order_by('-like_count')
            elif order2 == 'views':
                if order3 == 'reverse':
                    photos = photos.order_by('view_count')
                else:
                    photos = photos.order_by('-view_count')
            elif order2 == 'datings':
                if order3 == 'reverse':
                    photos = photos.order_by('dating_count')
                else:
                    photos = photos.order_by('-dating_count')
        elif order1 == 'time':
            if order2 == 'rephotos':
                if order3 == 'reverse':
                    photos = photos.extra(select={'first_rephoto_is_null': 'project_photo.first_rephoto IS NULL', },
                                          order_by=['first_rephoto_is_null', 'project_photo.first_rephoto'], )
                else:
                    photos = photos.extra(select={'latest_rephoto_is_null': 'project_photo.latest_rephoto IS NULL', },
                                          order_by=['latest_rephoto_is_null', '-project_photo.latest_rephoto'], )
                photos_with_rephotos = photos.filter(rephoto_count__gt=0).count()
            elif order2 == 'comments':
                if order3 == 'reverse':
                    photos = photos.extra(select={'first_comment_is_null': 'project_photo.first_comment IS NULL', },
                                          order_by=['first_comment_is_null', 'project_photo.first_comment'], )
                else:
                    photos = photos.extra(select={'latest_comment_is_null': 'project_photo.latest_comment IS NULL', },
                                          order_by=['latest_comment_is_null', '-project_photo.latest_comment'], )
                photos_with_comments = photos.filter(comment_count__gt=0).count()
            elif order2 == 'geotags':
                if order3 == 'reverse':
                    photos = photos.extra(select={'first_geotag_is_null': 'project_photo.first_geotag IS NULL', },
                                          order_by=['first_geotag_is_null', 'project_photo.first_geotag'], )
                else:
                    photos = photos.extra(select={'latest_geotag_is_null': 'project_photo.latest_geotag IS NULL', },
                                          order_by=['latest_geotag_is_null', '-project_photo.latest_geotag'], )
            elif order2 == 'likes':
                if order3 == 'reverse':
                    photos = photos.extra(select={'first_like_is_null': 'project_photo.first_like IS NULL', },
                                          order_by=['first_like_is_null', 'project_photo.first_like'], )
                else:
                    photos = photos.extra(select={'latest_like_is_null': 'project_photo.latest_like IS NULL', },
                                          order_by=['latest_like_is_null', '-project_photo.latest_like'], )
            elif order2 == 'views':
                if order3 == 'reverse':
                    photos = photos.extra(select={'first_view_is_null': 'project_photo.first_view IS NULL', },
                                          order_by=['first_view_is_null', 'project_photo.first_view'], )
                else:
                    photos = photos.extra(select={'latest_view_is_null': 'project_photo.latest_view IS NULL', },
                                          order_by=['latest_view_is_null', '-project_photo.latest_view'], )
            elif order2 == 'datings':
                if order3 == 'reverse':
                    photos = photos.extra(select={'first_dating_is_null': 'project_photo.first_dating IS NULL', },
                                          order_by=['first_dating_is_null', 'project_photo.first_dating'], )
                else:
                    photos = photos.extra(select={'latest_dating_is_null': 'project_photo.latest_dating IS NULL', },
                                          order_by=['latest_dating_is_null', '-project_photo.latest_dating'], )
            elif order2 == 'stills':
                if order3 == 'reverse':
                    photos = photos.order_by('-video_timestamp')
                else:
                    photos = photos.order_by('video_timestamp')
            elif order2 == 'added':
                if order3 == 'reverse':
                    photos = photos.order_by('created')
                else:
                    photos = photos.order_by('-created')
                if order1 == 'time':
                    default_ordering = True
        else:
            if order3 == 'reverse':
                photos = photos.order_by('created')
            else:
                photos = photos.order_by('-created')
        if requested_photo:
            ids = list(photos.values_list('id', flat=True))
            if requested_photo.id in ids:
                photo_count_before_requested = ids.index(requested_photo.id)
                page = ceil(float(photo_count_before_requested) / float(page_size))
        start = (page - 1) * page_size
        total = photos.count()
        if start < 0:
            start = 0
        if start > total:
            start = total
        if int(start + page_size) > total:
            end = total
        else:
            end = start + page_size
        end = int(end)
        max_page = ceil(float(total) / float(page_size))
        qs_for_fb = photos[:5]
        # FIXME: Stupid
        if order1 == 'amount' and order2 == 'geotags':
            photos = photos.values_list('id', 'width', 'height', 'description', 'lat', 'lon', 'azimuth',
                                        'rephoto_count',
                                        'comment_count', 'geotag_count', 'geotag_count', 'geotag_count', 'flip')[
                     start:end]
        elif order1 == 'closest' and lat and lon:
            photos = photos.values_list('id', 'width', 'height', 'description', 'lat', 'lon', 'azimuth',
                                        'rephoto_count',
                                        'comment_count', 'geotag_count', 'distance', 'geotag_count', 'flip')[
                     start:end]
        else:
            photos = photos.values_list('id', 'width', 'height', 'description', 'lat', 'lon', 'azimuth',
                                        'rephoto_count',
                                        'comment_count', 'geotag_count', 'geotag_count', 'geotag_count', 'flip')[
                     start:end]
        photos = map(list, photos)
        if default_ordering and album and album.ordered:
            album_photos_links_order = AlbumPhoto.objects.filter(album=album).order_by('pk').values_list('photo_id',
                                                                                                         flat=True)
            for each in album_photos_links_order:
                photos = sorted(photos, key=lambda x: x[0] == each)
        # FIXME: Replacing objects with arrays is not a good idea, the small speed boost isn't worth it
        for p in photos:
            if hasattr(p[10], 'm'):
                p[10] = p[10].m
            p[1], p[2] = calculate_thumbnail_size(p[1], p[2], 400)
            if 'photo_selection' in request.session:
                p[11] = 1 if str(p[0]) in request.session['photo_selection'] else 0
            else:
                p[11] = 0
            p.append(_get_pseudo_slug_for_photo(p[3], None, None))
        if album:
            ret['album'] = (
                album.id, album.name, ','.join(album.name.split(' ')), album.lat, album.lon, album.is_film_still_album)
            ret['videos'] = VideoSerializer(album.videos.all(), many=True).data
        else:
            ret['album'] = None
        fb_share_photos = []
        if requested_photo:
            ret['photo'] = [requested_photo.pk, requested_photo.get_pseudo_slug(), requested_photo.width,
                            requested_photo.height]
            fb_share_photos = [[requested_photo.pk, requested_photo.get_pseudo_slug(), requested_photo.width,
                                requested_photo.height]]
        else:
            ret['photo'] = None
            for p in qs_for_fb:
                fb_share_photos.append([p.pk, p.get_pseudo_slug(), p.width, p.height])
        ret['photos'] = photos
        ret['show_photos'] = show_photos
        # FIXME: DRY
        ret['fb_share_photos'] = fb_share_photos
        ret['start'] = start
        ret['end'] = end
        ret['photos_with_comments'] = photos_with_comments
        ret['photos_with_rephotos'] = photos_with_rephotos
        ret['order1'] = order1
        ret['order2'] = order2
        ret['order3'] = order3
        ret['page'] = page
        ret['total'] = total
        ret['max_page'] = max_page
        ret['my_likes_only'] = my_likes_only
        ret['rephotos_by'] = rephotos_by
        ret['rephotos_by_name'] = rephotos_by_name
    else:
        ret['album'] = None
        ret['photo'] = None
        ret['rephotos_by'] = None
        ret['rephotos_by_name'] = None
        ret['photos_with_comments'] = photos.filter(comment_count__isnull=False).count()
        ret['photos_with_rephotos'] = photos.filter(rephoto_count__isnull=False).count()
        qs_for_fb = photos[:5]
        photos = photos.values_list('id', 'width', 'height', 'description', 'lat', 'lon', 'azimuth',
                                    'rephoto_count', 'comment_count', 'geotag_count', 'geotag_count',
                                    'geotag_count')[0:page_size]
        ret['order1'] = 'time'
        ret['order2'] = 'added'
        ret['order3'] = None
        ret['is_photoset'] = False
        ret['my_likes_only'] = False
        ret['rephotos_by'] = None
        ret['total'] = photos.count()
        photos = map(list, photos)
        for p in photos:
            p[1], p[2] = calculate_thumbnail_size(p[1], p[2], 400)
            if 'photo_selection' in request.session:
                p[11] = 1 if str(p[0]) in request.session['photo_selection'] else 0
            else:
                p[11] = 0
        fb_share_photos = []
        for p in qs_for_fb:
            fb_share_photos.append([p.pk, p.get_pseudo_slug(), p.width, p.height])
        ret['fb_share_photos'] = fb_share_photos
        ret['photos'] = photos
        ret['start'] = 0
        ret['end'] = page_size
        ret['page'] = 1
        ret['show_photos'] = False
        ret['max_page'] = ceil(float(ret['total']) / float(page_size))

    return ret


def photo_selection(request):
    form = PhotoSelectionForm(request.POST)
    if 'photo_selection' not in request.session:
        request.session['photo_selection'] = {}
    if form.is_valid():
        if form.cleaned_data['clear']:
            request.session['photo_selection'] = {}
        elif form.cleaned_data['id']:
            photo_id = str(form.cleaned_data['id'].id)
            helper = request.session['photo_selection']
            if photo_id not in request.session['photo_selection']:
                helper[photo_id] = True
            else:
                del helper[photo_id]
            request.session['photo_selection'] = helper

    return HttpResponse(json.dumps(request.session['photo_selection']), content_type="application/json")


def list_photo_selection(request):
    photos = None
    at_least_one_photo_has_location = False
    count_with_location = 0
    whole_set_albums_selection_form = CuratorWholeSetAlbumsSelectionForm()
    if 'photo_selection' in request.session:
        photos = Photo.objects.filter(pk__in=request.session['photo_selection']).values_list('id', 'width', 'height',
                                                                                             'flip', 'description',
                                                                                             'lat', 'lon')
        photos = map(list, photos)
        for p in photos:
            if p[5] and p[6]:
                at_least_one_photo_has_location = True
                count_with_location += 1
            p[1], p[2] = calculate_thumbnail_size_max_height(p[1], p[2], 300)

    return render_to_response('photo_selection.html', RequestContext(request, {
        'is_selection': True,
        'photos': photos,
        'at_least_one_photo_has_location': at_least_one_photo_has_location,
        'count_with_location': count_with_location,
        'whole_set_albums_selection_form': whole_set_albums_selection_form
    }))


def upload_photo_selection(request):
    form = SelectionUploadForm(request.POST)
    album_selection_form = CuratorWholeSetAlbumsSelectionForm(request.POST)
    ret = {
        'error': False
    }
    profile = request.get_user().profile
    if form.is_valid() and profile.is_legit() and album_selection_form.is_valid():
        albums = album_selection_form.cleaned_data['albums']
        photo_ids = json.loads(form.cleaned_data['selection'])
        if len(albums) > 0:
            pass
        else:
            ret['error'] = _('Cannot upload to these albums')
        if len(albums) > 0:
            for a in albums:
                for pid in photo_ids:
                    existing_link = AlbumPhoto.objects.filter(album=a, photo_id=pid).first()
                    if not existing_link:
                        new_album_photo_link = AlbumPhoto(
                            photo=Photo.objects.get(pk=pid),
                            album=a,
                            profile=profile,
                            type=AlbumPhoto.RECURATED
                        )
                        Points(user=profile, action=Points.PHOTO_RECURATION, photo_id=pid, points=30, album=a,
                               created=datetime.datetime.now()).save()
                        new_album_photo_link.save()
                a.save()
            profile.set_calculated_fields()
            profile.save()
            ret['message'] = _('Recuration successful')
        else:
            ret['error'] = _('Problem with album selection')
    else:
        ret['error'] = _('Faulty data submitted')

    return HttpResponse(json.dumps(ret), content_type="application/json")


# FIXME: This should either be used more or not at all
def _make_fullscreen(p):
    if p and p.image:
        return {"url": p.image.url, "size": [p.image.width, p.image.height]}


def videoslug(request, video_id, pseudo_slug=None):
    video = get_object_or_404(Video, pk=video_id)
    if request.is_ajax():
        template = '_video_modal.html'
    else:
        template = 'videoview.html'

    return render_to_response(template, RequestContext(request, {
        'video': video,
    }))


def photoslug(request, photo_id=None, pseudo_slug=None):
    # Because of some bad design decisions, we have a URL /photo, let's just give a random photo
    if photo_id is None:
        photo_id = Photo.objects.order_by('?').first().pk
    # TODO: Should replace slug with correct one, many thing to keep in mind though: Google indexing, Facebook shares, comments, likes etc.
    profile = request.get_user().profile
    photo_obj = get_object_or_404(Photo, id=photo_id)

    user_has_likes = profile.likes.count() > 0
    user_has_rephotos = profile.photos.filter(rephoto_of__isnull=False).count() > 0

    # switch places if rephoto url
    rephoto = None
    first_rephoto = None
    if hasattr(photo_obj, "rephoto_of") and photo_obj.rephoto_of is not None:
        rephoto = photo_obj
        photo_obj = photo_obj.rephoto_of

    geotag_count = 0
    azimuth_count = 0
    original_thumb_size = None
    first_geotaggers = []
    if photo_obj:
        original_thumb_size = get_thumbnail(photo_obj.image, '1024x1024').size
        geotags = GeoTag.objects.filter(photo_id=photo_obj.id).distinct("user_id").order_by("user_id", "-created")
        geotag_count = geotags.count()
        if geotag_count > 0:
            correct_geotags_from_authenticated_users = geotags.exclude(user__pk=profile.user_id).filter(
                Q(user__first_name__isnull=False, user__last_name__isnull=False, is_correct=True))[:3]
            if len(correct_geotags_from_authenticated_users) > 0:
                for each in correct_geotags_from_authenticated_users:
                    first_geotaggers.append([each.user.get_display_name(), each.lat, each.lon, each.azimuth])
            first_geotaggers = json.dumps(first_geotaggers)
        azimuth_count = geotags.filter(azimuth__isnull=False).count()
        first_rephoto = photo_obj.rephotos.all().first()
        if 'user_view_array' not in request.session:
            request.session['user_view_array'] = []
        if photo_obj.id not in request.session['user_view_array']:
            photo_obj.view_count += 1
        now = datetime.datetime.now()
        if not photo_obj.first_view:
            photo_obj.first_view = now
        photo_obj.latest_view = now
        photo_obj.light_save()
        request.session['user_view_array'].append(photo_obj.id)
        request.session.modified = True

    is_frontpage = False
    is_mapview = False
    is_selection = False
    site = Site.objects.get_current()
    if request.is_ajax():
        template = "_photo_modal.html"
        if request.GET.get("isFrontpage"):
            is_frontpage = True
        if request.GET.get("isMapview"):
            is_mapview = True
        if request.GET.get('isSelection'):
            is_selection = True
    else:
        template = "photoview.html"
    if not photo_obj.description:
        title = "Unknown photo"
    else:
        title = " ".join(photo_obj.description.split(" ")[:5])[:50]
        if photo_obj.author:
            title += u' – ' + photo_obj.author

    album_ids = AlbumPhoto.objects.filter(photo_id=photo_obj.id).values_list("album_id", flat=True)
    full_album_id_list = list(album_ids)
    albums = Album.objects.filter(pk__in=album_ids, atype=Album.CURATED).prefetch_related('subalbum_of')
    for each in albums:
        if each.subalbum_of:
            current_parent = each.subalbum_of
            while current_parent is not None:
                full_album_id_list.append(current_parent.id)
                current_parent = current_parent.subalbum_of
    albums = Album.objects.filter(pk__in=full_album_id_list, atype=Album.CURATED)
    for a in albums:
        first_albumphoto = AlbumPhoto.objects.filter(photo_id=photo_obj.id, album=a).first()
        if first_albumphoto:
            a.this_photo_curator = first_albumphoto.profile
    album = albums.first()
    next_photo = None
    previous_photo = None
    if album:
        album_selection_form = AlbumSelectionForm({"album": album.id})
        if not request.is_ajax():
            next_photo = album.photos.filter(pk__gt=photo_obj.pk).order_by('pk').first()
            previous_photo = album.photos.filter(pk__lt=photo_obj.pk).order_by('pk').first()
    else:
        album_selection_form = AlbumSelectionForm()
        if not request.is_ajax():
            next_photo = Photo.objects.filter(pk__gt=photo_obj.pk).order_by('pk').first()
            previous_photo = Photo.objects.filter(pk__lt=photo_obj.pk).order_by('pk').first()

    if album:
        album = (album.id, album.lat, album.lon)

    rephoto_fullscreen = None
    if first_rephoto is not None:
        rephoto_fullscreen = _make_fullscreen(first_rephoto)

    photo_obj.tags = ','.join(photo_obj.description.split(' '))
    if rephoto and rephoto.description:
        rephoto.tags = ','.join(rephoto.description.split(' '))

    if 'photo_selection' in request.session:
        if str(photo_obj.id) in request.session['photo_selection']:
            photo_obj.in_selection = True

    user_confirmed_this_location = 'false'
    user_has_geotagged = GeoTag.objects.filter(photo=photo_obj, user=profile).exists()
    if user_has_geotagged:
        user_has_geotagged = 'true'
    else:
        user_has_geotagged = 'false'
    last_user_confirm_geotag_for_this_photo = GeoTag.objects.filter(type=GeoTag.CONFIRMATION, photo=photo_obj,
                                                                    user=profile) \
        .order_by('-created').first()
    if last_user_confirm_geotag_for_this_photo:
        if last_user_confirm_geotag_for_this_photo.lat == photo_obj.lat and last_user_confirm_geotag_for_this_photo.lon == photo_obj.lon:
            user_confirmed_this_location = 'true'

    photo_obj.user_likes = False
    photo_obj.user_loves = False
    likes = PhotoLike.objects.filter(photo=photo_obj)
    photo_obj.like_count = likes.distinct('profile').count()
    like = likes.filter(profile=profile).first()
    if like:
        if like.level == 1:
            photo_obj.user_likes = True
        elif like.level == 2:
            photo_obj.user_loves = True

    previous_datings = photo_obj.datings.order_by('created').prefetch_related('confirmations')
    for each in previous_datings:
        each.this_user_has_confirmed = each.confirmations.filter(profile=profile).exists()
    serialized_datings = DatingSerializer(previous_datings, many=True).data
    serialized_datings = JSONRenderer().render(serialized_datings)

    strings = []
    if photo_obj.source:
        strings = [photo_obj.source.description, photo_obj.source_key]
    desc = ' '.join(filter(None, strings))

    return render(request, template, {
        "photo": photo_obj,
        "previous_datings": serialized_datings,
        "datings_count": previous_datings.count(),
        "original_thumb_size": original_thumb_size,
        "user_confirmed_this_location": user_confirmed_this_location,
        "user_has_geotagged": user_has_geotagged,
        "fb_url": request.build_absolute_uri(reverse("project.ajapaik.views.photoslug", args=(photo_obj.id,))),
        "licence": Licence.objects.get(url="https://creativecommons.org/licenses/by-sa/4.0/"),
        "area": photo_obj.area,
        "album": album,
        "albums": albums,
        "is_frontpage": is_frontpage,
        "is_mapview": is_mapview,
        "is_selection": is_selection,
        "album_selection_form": album_selection_form,
        "geotag_count": geotag_count,
        "azimuth_count": azimuth_count,
        "fullscreen": _make_fullscreen(photo_obj),
        "rephoto_fullscreen": rephoto_fullscreen,
        "title": title,
        "description": desc,
        "rephoto": rephoto,
        "hostname": "https://%s" % (site.domain,),
        "first_geotaggers": first_geotaggers,
        "is_photoview": True,
        "ajapaik_facebook_link": settings.AJAPAIK_FACEBOOK_LINK,
        "user_has_likes": user_has_likes,
        "user_has_rephotos": user_has_rephotos,
        "next_photo": next_photo,
        "previous_photo": previous_photo
    })


def mapview_photo_upload_modal(request, photo_id):
    photo = get_object_or_404(Photo, pk=photo_id)
    licence = Licence.objects.get(url="https://creativecommons.org/licenses/by-sa/4.0/")
    return render_to_response('_photo_upload_modal.html', RequestContext(request, {
        'photo': photo,
        'licence': licence,
        'next': request.META["HTTP_REFERER"]
    }))


def pane_contents(request):
    # TODO: Form
    marker_ids = request.POST.getlist("marker_ids[]")

    data = []
    for p in Photo.objects.filter(lat__isnull=False, lon__isnull=False, rephoto_of__isnull=True, id__in=marker_ids) \
            .prefetch_related('rephotos').annotate(rephoto_count=Count('rephotos')).order_by('?') \
            .values_list('id', 'rephoto_count', 'flip', 'description', 'azimuth', 'comment_count', 'width',
                         'height'):
        pseudo_slug = _get_pseudo_slug_for_photo(p[3], None, None)
        im_url = reverse("project.ajapaik.views.image_thumb", args=(p[0], 400, pseudo_slug))
        permalink = reverse("project.ajapaik.views.photoslug", args=(p[0], pseudo_slug))
        width, height = calculate_thumbnail_size(p[6], p[7], 400)
        in_selection = False
        if 'photo_selection' in request.session:
            in_selection = str(p[0]) in request.session['photo_selection']
        data.append({
            "id": p[0],
            "url": im_url,
            "permalink": permalink,
            "rephotos": p[1],
            "flipped": p[2],
            "description": p[3],
            "azimuth": p[4],
            "width": width,
            "height": height,
            "comments": p[5],
            "in_selection": in_selection
        })

    return HttpResponse(json.dumps(data), content_type="application/json")


@ensure_csrf_cookie
def mapview(request, photo_id=None, rephoto_id=None):
    profile = request.get_user().profile
    area_selection_form = AreaSelectionForm(request.GET)
    game_album_selection_form = GameAlbumSelectionForm(request.GET)
    albums = _get_album_choices()
    photos_qs = Photo.objects.filter(rephoto_of__isnull=True)

    user_has_likes = profile.likes.count() > 0
    user_has_rephotos = profile.photos.filter(rephoto_of__isnull=False).count() > 0

    area = None
    album = None
    if area_selection_form.is_valid():
        area = area_selection_form.cleaned_data["area"]
        photos_qs = photos_qs.filter(area=area)

    if game_album_selection_form.is_valid():
        album = game_album_selection_form.cleaned_data["album"]
        photos_qs = album.photos.prefetch_related('subalbums')
        for sa in album.subalbums.exclude(atype=Album.AUTO):
            photos_qs = photos_qs | sa.photos.filter(rephoto_of__isnull=True)

    selected_photo = None
    selected_rephoto = None
    if rephoto_id:
        selected_rephoto = Photo.objects.filter(pk=rephoto_id).first()

    if photo_id:
        selected_photo = Photo.objects.filter(pk=photo_id).first()
    else:
        if selected_rephoto:
            selected_photo = Photo.objects.filter(pk=selected_rephoto.rephoto_of.id).first()

    if selected_photo and album is None:
        photo_album_ids = AlbumPhoto.objects.filter(photo_id=selected_photo.id).values_list("album_id", flat=True)
        album = Album.objects.filter(pk__in=photo_album_ids, is_public=True).order_by("-created").first()
        if album:
            photos_qs = album.photos.prefetch_related('subalbums').filter(rephoto_of__isnull=True)
            for sa in album.subalbums.exclude(atype=Album.AUTO):
                photos_qs = photos_qs | sa.photos.filter(rephoto_of__isnull=True)

    if selected_photo and area is None:
        area = Area.objects.filter(pk=selected_photo.area_id).first()
        photos_qs = photos_qs.filter(area=area).filter(rephoto_of__isnull=True)

    geotagging_user_count = GeoTag.objects.filter(photo_id__in=photos_qs.values_list('id', flat=True)).distinct(
        'user').count()
    geotagged_photo_count = photos_qs.distinct('id').filter(lat__isnull=False, lon__isnull=False).count()

    site = Site.objects.get_current()
    ret = {"area": area, "last_geotagged_photo_id": Photo.objects.order_by('-latest_geotag').first().id,
           "total_photo_count": photos_qs.distinct('id').count(), "geotagging_user_count": geotagging_user_count,
           "geotagged_photo_count": geotagged_photo_count, "albums": albums, "hostname": "https://%s" % (site.domain,),
           "selected_photo": selected_photo, "selected_rephoto": selected_rephoto, "is_mapview": True,
           "ajapaik_facebook_link": settings.AJAPAIK_FACEBOOK_LINK, "album": None, "user_has_likes": user_has_likes,
           "user_has_rephotos": user_has_rephotos}

    if album is not None:
        ret["album"] = (album.id, album.name, album.lat, album.lon, ','.join(album.name.split(' ')))
        ret["title"] = album.name + " - " + _("Browse photos on map")
        ret["facebook_share_photos"] = []
        facebook_share_photos = album.photos.all()[:5]
        for each in facebook_share_photos:
            each = [each.pk, each.get_pseudo_slug(), each.width, each.height]
            ret["facebook_share_photos"].append(each)
    elif area is not None:
        ret["title"] = area.name + " - " + _("Browse photos on map")
    else:
        ret["title"] = _("Browse photos on map")

    return render_to_response("mapview.html", RequestContext(request, ret))


def map_objects_by_bounding_box(request):
    form = MapDataRequestForm(request.POST)

    if form.is_valid():
        album = form.cleaned_data['album']
        area = form.cleaned_data['area']
        limit_by_album = form.cleaned_data['limit_by_album']
        sw_lat = form.cleaned_data['sw_lat']
        sw_lon = form.cleaned_data['sw_lon']
        ne_lat = form.cleaned_data['ne_lat']
        ne_lon = form.cleaned_data['ne_lon']
        # dating_start = form.cleaned_data['starting']
        # dating_end = form.cleaned_data['ending']

        qs = Photo.objects.filter(lat__isnull=False, lon__isnull=False, rephoto_of__isnull=True) \
            .annotate(rephoto_count=Count('rephotos'))

        if album and limit_by_album:
            album_photo_ids = album.get_historic_photos_queryset_with_subalbums().values_list('id', flat=True)
            qs = qs.filter(id__in=album_photo_ids)

        if area:
            qs = qs.filter(area=area)

        if sw_lat and sw_lon and ne_lat and ne_lon:
            qs = qs.filter(lat__gte=sw_lat, lon__gte=sw_lon, lat__lte=ne_lat, lon__lte=ne_lon)

            # if dating_start:
            # qs = qs.annotate(min_start=Max('datings__start')).filter(min_start__gte=dating_start)

            # if dating_end:
            # qs = qs.annotate(max_end=Min('datings__end')).filter(max_end__lte=dating_end)

        qs = qs.values_list('id', 'lat', 'lon', 'azimuth', 'rephoto_count')

        photos = []
        # TODO: Normal serialization
        for p in qs:
            photos.append([p[0], p[1], p[2], p[3], p[4]])

        data = {'photos': photos}
    else:
        data = {'photos': []}

    return HttpResponse(json.dumps(data), content_type='application/json')


def geotag_add(request):
    submit_geotag_form = SubmitGeotagForm(request.POST)
    profile = request.get_user().profile
    ret = {}
    if submit_geotag_form.is_valid():
        azimuth_score = 0
        new_geotag = submit_geotag_form.save(commit=False)
        new_geotag.user = profile
        trust = _calc_trustworthiness(profile.id)
        new_geotag.trustworthiness = trust
        tagged_photo = submit_geotag_form.cleaned_data['photo']
        if tagged_photo.flip is None:
            tagged_photo.flip = False
        # user flips, photo is flipped -> flip back
        # user flips, photo isn't flipped -> flip
        # user doesn't flip, photo is flipped -> leave flipped
        # user doesn't flip, photo isn't flipped -> leave as is
        if new_geotag.photo_flipped:
            most_trustworthy_geotag = tagged_photo.geotags.order_by('-trustworthiness').first()
            if not most_trustworthy_geotag or (
                        most_trustworthy_geotag
                    and most_trustworthy_geotag.trustworthiness < new_geotag.trustworthiness):
                tagged_photo.do_flip()
        new_geotag.save()
        initial_lat = tagged_photo.lat
        initial_lon = tagged_photo.lon
        # Calculate new lat, lon, confidence, guess_level, azimuth, azimuth_confidence, geotag_count for photo
        tagged_photo.set_calculated_fields()
        tagged_photo.latest_geotag = datetime.datetime.now()
        tagged_photo.save()
        processed_tagged_photo = Photo.objects.filter(pk=tagged_photo.id).get()
        ret['estimated_location'] = [processed_tagged_photo.lat, processed_tagged_photo.lon]
        if processed_tagged_photo.azimuth:
            ret['azimuth'] = processed_tagged_photo.azimuth
        processed_geotag = GeoTag.objects.filter(pk=new_geotag.id).get()
        if processed_geotag.origin == GeoTag.GAME:
            if len(tagged_photo.geotags.all()) == 1:
                score = max(20, int(300 * trust))
            else:
                # TODO: How bulletproof is this? 0 score geotags happen then and again
                try:
                    error_in_meters = distance_in_meters(tagged_photo.lon, tagged_photo.lat, processed_geotag.lon,
                                                         processed_geotag.lat)
                    score = int(130 * max(0, min(1, (1 - (error_in_meters - 15) / float(94 - 15)))))
                except TypeError:
                    score = 0
        else:
            score = int(trust * 100)
        if processed_geotag.hint_used:
            score *= 0.75
        if processed_geotag.azimuth_correct and tagged_photo.azimuth and processed_geotag.azimuth:
            degree_error_point_array = [100, 99, 97, 93, 87, 83, 79, 73, 67, 61, 55, 46, 37, 28, 19, 10]
            difference = int(angle_diff(tagged_photo.azimuth, processed_geotag.azimuth))
            if difference <= 15:
                azimuth_score = degree_error_point_array[int(difference)]
        processed_geotag.azimuth_score = azimuth_score
        processed_geotag.score = score + azimuth_score
        processed_geotag.save()
        # ret['is_correct'] = processed_geotag.is_correct
        ret['current_score'] = processed_geotag.score
        Points(user=profile, action=Points.GEOTAG, geotag=processed_geotag, points=processed_geotag.score,
               created=datetime.datetime.now(), photo=processed_geotag.photo).save()
        geotags_for_this_photo = GeoTag.objects.filter(photo=tagged_photo)
        ret['new_geotag_count'] = geotags_for_this_photo.distinct('user').count()
        ret['heatmap_points'] = [[x.lat, x.lon] for x in geotags_for_this_photo]
        # ret['azimuth_tags'] = geotags_for_this_photo.filter(azimuth__isnull=False).count()
        # ret['confidence'] = processed_tagged_photo.confidence
        profile.set_calculated_fields()
        profile.save()
        ret['feedback_message'] = ''
        processed_photo = Photo.objects.filter(pk=tagged_photo.pk).first()
        if processed_geotag.origin == GeoTag.GAME and processed_photo:
            if processed_photo.lat == initial_lat and processed_photo.lon == initial_lon:
                ret['feedback_message'] = _(
                    "Your contribution didn't change the estimated location for the photo, not yet anyway.")
            else:
                ret['feedback_message'] = _('The photo has been mapped to a new location thanks to you.')
            if len(geotags_for_this_photo) == 1:
                ret['feedback_message'] = _('Your guess was first.')
        for a in processed_photo.albums.all():
            qs = a.get_geotagged_historic_photo_queryset_with_subalbums()
            a.geotagged_photo_count_with_subalbums = qs.count()
            a.light_save()
    else:
        if 'lat' not in submit_geotag_form.cleaned_data and 'lon' not in submit_geotag_form.cleaned_data \
                and 'photo_id' in submit_geotag_form.data:
            Skip(user=profile, photo_id=submit_geotag_form.data['photo_id']).save()
            if 'user_skip_array' not in request.session:
                request.session['user_skip_array'] = []
            request.session['user_skip_array'].append(submit_geotag_form.data['photo_id'])
            request.session.modified = True

    return HttpResponse(json.dumps(ret), content_type='application/json')


def geotag_confirm(request):
    form = ConfirmGeotagForm(request.POST)
    profile = request.get_user().profile
    ret = {
        'message': 'OK'
    }
    if form.is_valid():
        p = form.cleaned_data['photo']
        # Check if user is eligible to confirm location (again)
        last_confirm_geotag_by_this_user_for_p = p.geotags.filter(user_id=profile.id, type=GeoTag.CONFIRMATION) \
            .order_by('-created').first()
        if not last_confirm_geotag_by_this_user_for_p or (p.lat and p.lon and (
                        last_confirm_geotag_by_this_user_for_p.lat != p.lat and last_confirm_geotag_by_this_user_for_p.lon != p.lon)):
            trust = _calc_trustworthiness(request.get_user().id)
            confirmed_geotag = GeoTag(
                lat=p.lat,
                lon=p.lon,
                origin=GeoTag.MAP_VIEW,
                type=GeoTag.CONFIRMATION,
                map_type=GeoTag.OPEN_STREETMAP,
                hint_used=True,
                user=profile,
                photo=p,
                is_correct=True,
                score=max(1, int(trust * 50)),
                azimuth_score=0,
                trustworthiness=trust
            )
            if p.azimuth:
                confirmed_geotag.azimuth = p.azimuth
                confirmed_geotag.azimuth_correct = True
            confirmed_geotag.save()
            Points(user=profile, action=Points.GEOTAG, geotag=confirmed_geotag, points=confirmed_geotag.score,
                   created=datetime.datetime.now(), photo=p).save()
            p.latest_geotag = datetime.datetime.now()
            p.save()
            profile.set_calculated_fields()
            profile.save()
        ret["new_geotag_count"] = GeoTag.objects.filter(photo=p).distinct('user').count()

    return HttpResponse(json.dumps(ret), content_type="application/json")


def leaderboard(request, album_id=None):
    # Leader-board with first position, one in front of you, your score and one after you
    album_leaderboard = None
    general_leaderboard = None
    profile = request.get_user().profile
    if album_id:
        # Album leader-board takes into account any users that have any contributions to the album
        album = get_object_or_404(Album, pk=album_id)
        # TODO: Almost identical code is used in many places, put under album model
        album_photos_qs = album.photos.all()
        for sa in album.subalbums.exclude(atype=Album.AUTO):
            album_photos_qs = album_photos_qs | sa.photos.all()
        album_photo_ids = set(album_photos_qs.values_list('id', flat=True))
        album_rephoto_ids = frozenset(album_photos_qs.filter(rephoto_of__isnull=False)
                                      .values_list('rephoto_of_id', flat=True))
        photo_points = Points.objects.filter(
            Q(photo_id__in=album_photo_ids) | Q(photo_id__in=album_rephoto_ids)).exclude(
            action=Points.PHOTO_RECURATION)
        photo_points = photo_points | Points.objects.filter(photo_id__in=album_photo_ids, album=album,
                                                            action=Points.PHOTO_RECURATION)
        user_score_map = {}
        for each in photo_points:
            if each.user_id in user_score_map:
                user_score_map[each.user_id] += each.points
            else:
                user_score_map[each.user_id] = each.points
        if profile.id not in user_score_map:
            user_score_map[profile.id] = 0
        sorted_scores = sorted(user_score_map.items(), key=operator.itemgetter(1), reverse=True)
        pk_list = [x[0] for x in sorted_scores]
        current_user_rank = pk_list.index(profile.id)
        if current_user_rank == -1:
            current_user_rank = len(sorted_scores)
        current_user_rank += 1
        # Works on Postgres, we don't really need to worry about this I guess...maybe only if it gets slow
        clauses = ' '.join(['WHEN user_id=%s THEN %s' % (pk, i) for i, pk in enumerate(pk_list)])
        ordering = 'CASE %s END' % clauses
        top_users = Profile.objects.filter(Q(user_id__in=pk_list) | Q(user_id=profile.id)) \
            .extra(select={'ordering': ordering}, order_by=('ordering',))
        start = current_user_rank - 2
        if start < 0:
            start = 0
        top_users = top_users[start:current_user_rank + 1]
        n = current_user_rank
        for each in top_users:
            if each.user_id == profile.id:
                each.is_current_user = True
            each.position = n
            each.custom_score = user_score_map[each.user_id]
            n += 1
        album_leaderboard = top_users
    else:
        _calculate_recent_activity_scores()
        profile_rank = Profile.objects.filter(score_recent_activity__gt=profile.score_recent_activity,
                                              first_name__isnull=False, last_name__isnull=False).count() + 1
        leaderboard_queryset = Profile.objects.filter(
            Q(first_name__isnull=False, last_name__isnull=False, score_recent_activity__gt=0) |
            Q(pk=profile.id)).order_by('-score_recent_activity')
        start = profile_rank - 2
        if start < 0:
            start = 0
        nearby_users = leaderboard_queryset[start:profile_rank + 1]
        n = start + 1
        for each in nearby_users:
            if each.user_id == profile.id:
                each.is_current_user = True
            each.position = n
            n += 1
        general_leaderboard = nearby_users
    if request.is_ajax():
        template = '_block_leaderboard.html'
    else:
        template = 'leaderboard.html'
    # FIXME: this shouldn't be necessary, there are easier ways to construct URLs
    site = Site.objects.get_current()
    return render_to_response(template, RequestContext(request, {
        'is_top_50': False,
        'title': _('Leaderboard'),
        'hostname': 'https://%s' % (site.domain,),
        'leaderboard': general_leaderboard,
        'album_leaderboard': album_leaderboard,
        'ajapaik_facebook_link': settings.AJAPAIK_FACEBOOK_LINK
    }))


def all_time_leaderboard(request):
    _calculate_recent_activity_scores()
    atl = _get_all_time_leaderboard50(request.get_user().profile.pk)
    template = ['', '_block_leaderboard.html', 'leaderboard.html'][request.is_ajax() and 1 or 2]
    site = Site.objects.get_current()
    return render_to_response(template, RequestContext(request, {
        'hostname': 'https://%s' % (site.domain,),
        'all_time_leaderboard': atl,
        'title': _('Leaderboard'),
        'is_top_50': True
    }))


def top50(request, album_id=None):
    _calculate_recent_activity_scores()
    profile = request.get_user().profile
    album_name = None
    album_leaderboard = None
    general_leaderboard = None
    if album_id:
        album_leaderboard, album_name = _get_album_leaderboard50(profile.pk, album_id)
    else:
        general_leaderboard = _get_all_time_leaderboard50(profile.pk)
    activity_leaderboard = Profile.objects.filter(
        Q(first_name__isnull=False, last_name__isnull=False, score_recent_activity__gt=0) |
        Q(pk=profile.id)).order_by('-score_recent_activity').prefetch_related('user')[:50]
    n = 1
    for each in activity_leaderboard:
        if each.user_id == profile.id:
            each.is_current_user = True
        each.position = n
        n += 1
    if request.is_ajax():
        template = '_block_leaderboard.html'
    else:
        template = 'leaderboard.html'
    site = Site.objects.get_current()
    return render_to_response(template, RequestContext(request, {
        'activity_leaderboard': activity_leaderboard,
        'album_name': album_name,
        'album_leaderboard': album_leaderboard,
        'all_time_leaderboard': general_leaderboard,
        'hostname': 'https://%s' % (site.domain,),
        'title': _('Leaderboard'),
        'is_top_50': True,
        'ajapaik_facebook_link': settings.AJAPAIK_FACEBOOK_LINK
    }))


def difficulty_feedback(request):
    user_profile = request.get_user().profile
    # FIXME: Form, better error handling
    if not user_profile:
        return HttpResponse("Error", status=500)
    user_trustworthiness = _calc_trustworthiness(user_profile.pk)
    user_last_geotag = GeoTag.objects.filter(user=user_profile).order_by("-created").first()
    level = request.POST.get("level") or None
    photo_id = request.POST.get("photo_id") or None
    # FIXME: Why so many lines?
    if user_profile and level and photo_id and user_last_geotag:
        feedback_object = DifficultyFeedback()
        feedback_object.user_profile = user_profile
        feedback_object.level = level
        feedback_object.photo_id = photo_id
        feedback_object.trustworthiness = user_trustworthiness
        feedback_object.geotag = user_last_geotag
        feedback_object.save()
        photo = Photo.objects.get(id=photo_id)
        # FIXME: Shouldn't use costly set_calculated_fields here, maybe send extra var to lighten it
        photo.set_calculated_fields()
        photo.save()

    return HttpResponse("OK")


def custom_404(request):
    response = render_to_response("404.html", {}, context_instance=RequestContext(request))
    response.status_code = 404
    return response


def custom_500(request):
    response = render_to_response("500.html", {}, context_instance=RequestContext(request))
    response.status_code = 500
    return response


def public_add_album(request):
    # FIXME: ModelForm
    add_album_form = AddAlbumForm(request.POST)
    if add_album_form.is_valid():
        user_profile = request.get_user().profile
        name = add_album_form.cleaned_data["name"]
        description = add_album_form.cleaned_data["description"]
        if user_profile:
            new_album = Album(
                name=name, description=description, atype=Album.COLLECTION, profile=user_profile, is_public=False)
            new_album.save()
            selectable_albums = Album.objects.filter(Q(atype=Album.FRONTPAGE) | Q(profile=user_profile))
            selectable_albums = [{"id": x.id, "name": x.name} for x in selectable_albums]
            return HttpResponse(json.dumps(selectable_albums), content_type="application/json")
    return HttpResponse(json.dumps("Error"), content_type="application/json", status=400)


def public_add_area(request):
    add_area_form = AddAreaForm(request.POST)
    # TODO: Better duplicate handling
    if add_area_form.is_valid():
        try:
            Area.objects.get(name=add_area_form.cleaned_data["name"])
        except ObjectDoesNotExist:
            user_profile = request.get_user().profile
            name = add_area_form.cleaned_data["name"]
            lat = add_area_form.cleaned_data["lat"]
            lon = add_area_form.cleaned_data["lon"]
            if user_profile:
                new_area = Area(name=name, lat=lat, lon=lon)
                new_area.save()
                selectable_areas = Area.objects.order_by('name').all()
                selectable_areas = [{'id': x.id, 'name': x.name} for x in selectable_areas]
                return HttpResponse(json.dumps(selectable_areas), content_type="application/json")
    return HttpResponse(json.dumps("Error"), content_type="application/json", status=400)


@ensure_csrf_cookie
def curator(request):
    last_created_album = Album.objects.filter(is_public=True).order_by('-created')[0]
    # FIXME: Ugly
    curator_random_image_ids = AlbumPhoto.objects.filter(
        album_id=last_created_album.id).order_by('?').values_list('photo_id', flat=True)
    if not curator_random_image_ids or len(curator_random_image_ids) < 5:
        curator_random_image_ids = AlbumPhoto.objects.order_by('?').values_list('photo_id', flat=True)
    curator_random_images = Photo.objects.filter(pk__in=curator_random_image_ids)[:5]
    site = Site.objects.get_current()
    return render_to_response('curator.html', RequestContext(request, {
        'description':
            _('Search for old photos, add them to Ajapaik, determine their locations and share the resulting album!'),
        'curator_random_images': curator_random_images,
        'title': _('Timepatch (Ajapaik) - curate'),
        'hostname': 'https://%s' % (site.domain,),
        'then_and_now_disabled': CURATOR_THEN_AND_NOW_CREATION_DISABLED,
        'is_curator': True,
        'CURATOR_FLICKR_ENABLED': CURATOR_FLICKR_ENABLED,
        'ajapaik_facebook_link': settings.AJAPAIK_FACEBOOK_LINK,
        'whole_set_albums_selection_form': CuratorWholeSetAlbumsSelectionForm()
    }))


def _curator_get_records_by_ids(ids):
    ids_str = ['"' + each + '"' for each in ids]
    request_params = '{"method":"getRecords","params":[[%s]],"id":0}' % ','.join(ids_str)
    response = requests.post(settings.AJAPAIK_VALIMIMOODUL_URL, data=request_params)
    response.encoding = 'utf-8'

    return response


def _join_2_json_objects(obj1, obj2):
    result = {'firstRecordViews': []}
    # TODO: Why do errors sometimes happen here?
    try:
        dict_a = json.loads(obj1)
        dict_b = json.loads(obj2)
        try:
            if 'result' in dict_a:
                for each in dict_a['result']['firstRecordViews']:
                    result['firstRecordViews'].append(each)
                if 'page' in dict_a['result']:
                    result['page'] = dict_a['result']['page']
                if 'pages' in dict_a['result']:
                    result['pages'] = dict_a['result']['pages']
                if 'ids' in dict_a['result']:
                    result['ids'] = dict_a['result']['ids']
            if 'result' in dict_b:
                for each in dict_b['result']['firstRecordViews']:
                    result['firstRecordViews'].append(each)
                if 'page' in dict_b['result']:
                    result['page'] = dict_b['result']['page']
                if 'pages' in dict_b['result']:
                    result['pages'] = dict_b['result']['pages']
                if 'ids' in dict_b['result']:
                    result['ids'] = dict_b['result']['ids']
        except TypeError:
            pass
    except TypeError:
        pass

    return json.dumps({'result': result})


def curator_search(request):
    form = CuratorSearchForm(request.POST)
    response = json.dumps({})
    flickr_driver = None
    valimimoodul_driver = None
    finna_driver = None
    if form.is_valid():
        if form.cleaned_data['useFlickr']:
            flickr_driver = FlickrCommonsDriver()
        if form.cleaned_data['useMUIS'] or form.cleaned_data['useMKA'] or form.cleaned_data['useDIGAR'] or \
                form.cleaned_data['useETERA'] or form.cleaned_data['useUTLIB']:
            valimimoodul_driver = ValimimoodulDriver()
            if form.cleaned_data['ids']:
                response = valimimoodul_driver.transform_response(
                    valimimoodul_driver.get_by_ids(form.cleaned_data['ids']),
                    form.cleaned_data['filterExisting'])
        if form.cleaned_data['useFinna']:
            finna_driver = FinnaDriver()
        if form.cleaned_data['fullSearch']:
            if valimimoodul_driver and not form.cleaned_data['ids']:
                response = _join_2_json_objects(response, valimimoodul_driver.transform_response(
                    valimimoodul_driver.search(form.cleaned_data), form.cleaned_data['filterExisting']))
            if flickr_driver:
                response = _join_2_json_objects(response, flickr_driver.transform_response(
                    flickr_driver.search(form.cleaned_data), form.cleaned_data['filterExisting']))
            if finna_driver:
                response = _join_2_json_objects(response, finna_driver.transform_response(
                    finna_driver.search(form.cleaned_data), form.cleaned_data['filterExisting'],
                    form.cleaned_data['flickrPage']))

    return HttpResponse(response, content_type="application/json")


def curator_my_album_list(request):
    user_profile = request.get_user().profile
    serializer = CuratorMyAlbumListAlbumSerializer(
        Album.objects.filter(Q(profile=user_profile, atype=Album.CURATED)).order_by("-created"), many=True
    )

    return HttpResponse(JSONRenderer().render(serializer.data), content_type="application/json")


def curator_selectable_albums(request):
    user_profile = request.get_user().profile
    serializer = CuratorAlbumSelectionAlbumSerializer(
        Album.objects.filter(((Q(profile=user_profile) | Q(is_public=True)) & ~Q(atype=Album.AUTO)) | (
            Q(open=True) & ~Q(atype=Album.AUTO))).order_by('name').all(), many=True
    )

    return HttpResponse(JSONRenderer().render(serializer.data), content_type="application/json")


def curator_selectable_parent_albums(request, album_id=None):
    user_profile = request.get_user().profile
    qs = Album.objects.filter(
        (Q(profile=user_profile, subalbum_of__isnull=True, is_public=True)) |
        (Q(open=True, subalbum_of__isnull=True))
    ).order_by('-created').all()
    if album_id:
        qs = qs.exclude(pk=album_id)
    serializer = CuratorAlbumSelectionAlbumSerializer(qs, many=True)

    return HttpResponse(JSONRenderer().render(serializer.data), content_type="application/json")


# TODO: Replace with Django REST API
def curator_get_album_info(request):
    album_id = request.POST.get("albumId") or None
    if album_id is not None:
        try:
            album = Album.objects.get(pk=album_id)
            serializer = CuratorAlbumInfoSerializer(album)
        except ObjectDoesNotExist:
            return HttpResponse("Album does not exist", status=404)
        return HttpResponse(JSONRenderer().render(serializer.data), content_type="application/json")
    return HttpResponse("No album ID", status=500)


# TODO: Replace with Django REST API
def curator_update_my_album(request):
    album_id = request.POST.get("albumId") or None
    user_profile = request.get_user().profile
    album_edit_form = CuratorAlbumEditForm(request.POST)
    if album_id is not None and user_profile and album_edit_form.is_valid():
        try:
            album = Album.objects.get(pk=album_id, profile=user_profile)
            album.name = album_edit_form.cleaned_data["name"]
            album.description = album_edit_form.cleaned_data["description"]
            album.open = album_edit_form.cleaned_data["open"]
            album.is_public = album_edit_form.cleaned_data["is_public"]
            if album_edit_form.cleaned_data['areaLat'] and album_edit_form.cleaned_data['areaLng']:
                album.lat = album_edit_form.cleaned_data['areaLat']
                album.lon = album_edit_form.cleaned_data['areaLng']
            parent_album = album_edit_form.cleaned_data["parent_album"]
            if parent_album:
                try:
                    parent_album = Album.objects.get(
                        Q(profile=user_profile, pk=parent_album.id) | Q(open=True, pk=parent_album.id))
                    album.subalbum_of = parent_album
                except ObjectDoesNotExist:
                    return HttpResponse("Faulty data", status=500)
            else:
                album.subalbum_of = None
            album.save()
            return HttpResponse("OK", status=200)
        except ObjectDoesNotExist:
            return HttpResponse("Album does not exist", status=404)

    return HttpResponse("Faulty data", status=500)


def curator_photo_upload_handler(request):
    profile = request.get_user().profile

    etera_token = request.POST.get("eteraToken")

    curator_album_selection_form = CuratorWholeSetAlbumsSelectionForm(request.POST)

    selection_json = request.POST.get("selection") or None
    selection = None
    # TODO: We need to override some values coming from sources, but we cannot really allow random stuff, what to do?
    # if selection_json is not None:
    #     # Query again to block porn
    #     parsed_selection = json.loads(selection_json)
    #     ids = [k for k, v in parsed_selection.iteritems()]
    #     response = _curator_get_records_by_ids(ids)
    #     parsed_response = json.loads(response.text)["result"]
    #     parsed_kv = {}
    #     for each in parsed_response:
    #         parsed_kv[each["id"]] = each
    #     for k, v in parsed_selection.iteritems():
    #         for sk, sv in parsed_kv[k].iteritems():
    #             # Some fields we don't want overwritten
    #             # FIXME: This now defeats the purpose of re-querying...
    #             if parsed_selection[k]["collections"] == 'DIGAR' and (sk == 'imageUrl' or sk == 'identifyingNumber'
    #                                                                   or sk == 'urlToRecord' or sk == 'institution'
    #                                                                   or sk == 'description'):
    #                 continue
    #             elif parsed_selection[k]['institution'] == 'ETERA' and (sk == 'identifyingNumber'):
    #                 continue
    #             else:
    #                 parsed_selection[k][sk] = sv
    #     selection = parsed_selection

    if selection_json is not None:
        selection = json.loads(selection_json)

    all_curating_points = []
    total_points_for_curating = 0
    ret = {
        "photos": {}
    }

    if selection and len(selection) > 0 and profile is not None and curator_album_selection_form.is_valid():
        general_albums = curator_album_selection_form.cleaned_data['albums']
        if len(general_albums) > 0:
            ret["album_id"] = general_albums[0].pk
        else:
            ret["album_id"] = None
        default_album = Album(
            name=str(profile.id) + "-" + str(datetime.datetime.now()),
            atype=Album.AUTO,
            profile=profile,
            is_public=False,
        )
        default_album.save()
        # 15 => unknown copyright
        unknown_licence = Licence.objects.get(pk=15)
        flickr_licence = Licence.objects.get(url='https://www.flickr.com/commons/usage/')
        for k, v in selection.iteritems():
            upload_form = CuratorPhotoUploadForm(v)
            created_album_photo_links = []
            awarded_curator_points = []
            if upload_form.is_valid():
                if upload_form.cleaned_data["institution"]:
                    if upload_form.cleaned_data["institution"] == 'Flickr Commons':
                        licence = flickr_licence
                    else:
                        # For Finna
                        if upload_form.cleaned_data["licence"]:
                            licence = Licence.objects.get_or_create(name=upload_form.cleaned_data["licence"])[0]
                        else:
                            licence = unknown_licence
                    upload_form.cleaned_data["institution"] = upload_form.cleaned_data["institution"].split(",")[0]
                    if upload_form.cleaned_data["institution"] == "ETERA":
                        upload_form.cleaned_data["institution"] = 'TLÜAR ETERA'
                    try:
                        source = Source.objects.get(description=upload_form.cleaned_data["institution"])
                    except ObjectDoesNotExist:
                        source = Source(
                            name=upload_form.cleaned_data["institution"],
                            description=upload_form.cleaned_data["institution"]
                        )
                        source.save()
                else:
                    licence = unknown_licence
                    source = Source.objects.get(name="AJP")
                existing_photo = None
                if upload_form.cleaned_data["id"] and upload_form.cleaned_data["id"] != "":
                    if upload_form.cleaned_data["collections"] == "DIGAR":
                        incoming_muis_id = upload_form.cleaned_data["identifyingNumber"]
                    else:
                        incoming_muis_id = upload_form.cleaned_data["id"]
                    if 'ETERA' in upload_form.cleaned_data["institution"]:
                        upload_form.cleaned_data["types"] = "Foto"
                    if '_' in incoming_muis_id:
                        muis_id = incoming_muis_id.split('_')[0]
                        muis_media_id = incoming_muis_id.split('_')[1]
                    else:
                        muis_id = incoming_muis_id
                        muis_media_id = None
                    if upload_form.cleaned_data["collections"] == "DIGAR":
                        upload_form.cleaned_data["identifyingNumber"] = 'nlib-digar:' + upload_form.cleaned_data[
                            "identifyingNumber"]
                        muis_media_id = 1
                    try:
                        if muis_media_id:
                            existing_photo = Photo.objects.filter(
                                source=source, external_id=muis_id, external_sub_id=muis_media_id).get()
                        else:
                            existing_photo = Photo.objects.filter(
                                source=source, external_id=muis_id).get()
                    except ObjectDoesNotExist:
                        pass
                    if not existing_photo:
                        new_photo = None
                        if upload_form.cleaned_data["date"] == "[]":
                            upload_form.cleaned_data["date"] = None
                        try:
                            new_photo = Photo(
                                user=profile,
                                author=upload_form.cleaned_data["creators"].encode('utf-8'),
                                description=upload_form.cleaned_data["title"].rstrip().encode('utf-8'),
                                source=source,
                                types=upload_form.cleaned_data["types"].encode('utf-8') if upload_form.cleaned_data[
                                    "types"] else None,
                                keywords=upload_form.cleaned_data["keywords"].strip().encode('utf-8') if
                                upload_form.cleaned_data["keywords"] else None,
                                date_text=upload_form.cleaned_data["date"].encode('utf-8') if
                                upload_form.cleaned_data["date"] else None,
                                licence=licence,
                                external_id=muis_id,
                                external_sub_id=muis_media_id,
                                source_key=upload_form.cleaned_data["identifyingNumber"],
                                source_url=upload_form.cleaned_data["urlToRecord"],
                                flip=upload_form.cleaned_data["flip"],
                                invert=upload_form.cleaned_data["invert"],
                                stereo=upload_form.cleaned_data["stereo"],
                                rotated=upload_form.cleaned_data["rotated"]
                            )
                            new_photo.save()
                            if upload_form.cleaned_data["collections"] == "DIGAR":
                                new_photo.image = 'uploads/DIGAR_' + str(new_photo.source_key).split(':')[1] + '_1.jpg'
                            else:
                                opener = urllib2.build_opener()
                                headers = [("User-Agent",
                                            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36")]
                                if etera_token:
                                    headers.append(("Authorization", "Bearer " + etera_token))
                                opener.addheaders = headers
                                img_response = opener.open(upload_form.cleaned_data["imageUrl"])
                                if 'ETERA' in new_photo.source.description:
                                    img = ContentFile(img_response.read())
                                    new_photo.image_no_watermark.save("etera.jpg", img)
                                    new_photo.watermark()
                                else:
                                    new_photo.image.save("muis.jpg", ContentFile(img_response.read()))
                            if new_photo.invert:
                                photo_path = settings.MEDIA_ROOT + "/" + str(new_photo.image)
                                img = Image.open(photo_path)
                                inverted_grayscale_image = ImageOps.invert(img).convert('L')
                                inverted_grayscale_image.save(photo_path)
                            if new_photo.rotated > 0:
                                photo_path = settings.MEDIA_ROOT + "/" + str(new_photo.image)
                                img = Image.open(photo_path)
                                rot = img.rotate(new_photo.rotated, expand=1)
                                rot.save(photo_path)
                                new_photo.width, new_photo.height = rot.size
                            if new_photo.flip:
                                photo_path = settings.MEDIA_ROOT + "/" + str(new_photo.image)
                                img = Image.open(photo_path)
                                flipped_image = img.transpose(Image.FLIP_LEFT_RIGHT)
                                flipped_image.save(photo_path)
                            ret["photos"][k] = {}
                            ret["photos"][k]["message"] = _("OK")
                            lat = upload_form.cleaned_data["latitude"]
                            lng = upload_form.cleaned_data["longitude"]
                            if lat and lng and not GeoTag.objects.filter(type=GeoTag.SOURCE_GEOTAG,
                                                                         photo__source_key=new_photo.source_key).exists():
                                source_geotag = GeoTag(
                                    lat=lat,
                                    lon=lng,
                                    origin=GeoTag.SOURCE,
                                    type=GeoTag.SOURCE_GEOTAG,
                                    map_type=GeoTag.NO_MAP,
                                    photo=new_photo,
                                    is_correct=True,
                                    trustworthiness=0.07
                                )
                                source_geotag.save()
                                new_photo.latest_geotag = source_geotag.created
                                new_photo.set_calculated_fields()
                            new_photo.save()
                            points_for_curating = Points(action=Points.PHOTO_CURATION, photo=new_photo, points=50,
                                                         user=profile, created=new_photo.created,
                                                         album=general_albums[0])
                            points_for_curating.save()
                            awarded_curator_points.append(points_for_curating)
                            if len(general_albums) > 0:
                                for a in general_albums:
                                    ap = AlbumPhoto(photo=new_photo, album=a, profile=profile, type=AlbumPhoto.CURATED)
                                    ap.save()
                                    created_album_photo_links.append(ap)
                                    if not a.cover_photo:
                                        a.cover_photo = new_photo
                                        a.light_save()
                                for b in general_albums[1:]:
                                    points_for_curating = Points(action=Points.PHOTO_RECURATION, photo=new_photo,
                                                                 points=30,
                                                                 user=profile, created=new_photo.created,
                                                                 album=b)
                                    points_for_curating.save()
                                    awarded_curator_points.append(points_for_curating)
                                    all_curating_points.append(points_for_curating)
                            ap = AlbumPhoto(photo=new_photo, album=default_album, profile=profile,
                                            type=AlbumPhoto.CURATED)
                            ap.save()
                            created_album_photo_links.append(ap)
                            ret["photos"][k]["success"] = True
                            all_curating_points.append(points_for_curating)
                        except:
                            if new_photo:
                                new_photo.image.delete()
                                new_photo.delete()
                            for ap in created_album_photo_links:
                                ap.delete()
                            for cp in awarded_curator_points:
                                cp.delete()
                            ret["photos"][k] = {}
                            ret["photos"][k]["error"] = _("Error uploading file")
                    else:
                        if len(general_albums) > 0:
                            for a in general_albums:
                                ap = AlbumPhoto(photo=existing_photo, album=a, profile=profile,
                                                type=AlbumPhoto.RECURATED)
                                ap.save()
                                points_for_recurating = Points(user=profile, action=Points.PHOTO_RECURATION,
                                                               photo=existing_photo, points=30,
                                                               album=general_albums[0], created=datetime.datetime.now())
                                points_for_recurating.save()
                                all_curating_points.append(points_for_recurating)
                        dap = AlbumPhoto(photo=existing_photo, album=default_album, profile=profile,
                                         type=AlbumPhoto.RECURATED)
                        dap.save()
                        ret["photos"][k] = {}
                        ret["photos"][k]["success"] = True
                        ret["photos"][k]["message"] = _("Photo already exists in Ajapaik")
                        # else:
                        #     print upload_form.errors
        if general_albums:
            for ga in general_albums:
                requests.post("https://graph.facebook.com/v2.3/?id=" + (
                    request.build_absolute_uri(reverse("project.ajapaik.views.game")) + "?album=" + str(
                        ga.id)) + "&scrape=true")
        for cp in all_curating_points:
            total_points_for_curating += cp.points
        ret["total_points_for_curating"] = total_points_for_curating
        if len(general_albums) > 0:
            for album in general_albums:
                album.save()
                if album.subalbum_of:
                    album.subalbum_of.save()
    else:
        if not selection or len(selection) == 0:
            error = _("Please add photos to your album")
        else:
            error = _("Not enough data submitted")
        ret = {
            "error": error
        }
    return HttpResponse(json.dumps(ret), content_type="application/json")


def update_like_state(request):
    profile = request.get_user().profile
    form = PhotoLikeForm(request.POST)
    ret = {}
    if form.is_valid() and profile:
        p = form.cleaned_data['photo']
        like = PhotoLike.objects.filter(photo=p, profile=profile).first()
        if like:
            if like.level == 1:
                like.level = 2
                like.save()
                ret['level'] = 2
            elif like.level == 2:
                like.delete()
                ret['level'] = 0
                p.first_like = None
                p.latest_list = None
        else:
            like = PhotoLike(
                profile=profile,
                photo=p,
                level=1
            )
            like.save()
            ret['level'] = 1
        like_sum = p.likes.aggregate(Sum('level'))['level__sum']
        if not like_sum:
            like_sum = 0
        like_count = p.likes.distinct('profile').count()
        ret['likeCount'] = like_count
        p.like_count = like_sum
        if like_count > 0:
            first_like = p.likes.order_by('created').first()
            latest_like = p.likes.order_by('-created').first()
            if first_like:
                p.first_like = first_like.created
            if latest_like:
                p.latest_like = latest_like.created
        else:
            p.first_like = None
            p.latest_like = None
        p.light_save()

    return HttpResponse(json.dumps(ret), content_type="application/json")


@user_passes_test(lambda u: u.groups.filter(name='csv_uploaders').count() == 1, login_url='/admin/')
def csv_upload(request):
    import csv
    import zipfile
    import hashlib
    profile = request.get_user().profile
    csv_file = request.FILES['csv_file']
    # Broke for some reason
    # dialect = csv.Sniffer().sniff(csv_file.read(1024), delimiters=';,')
    header_row = None
    photos_metadata = {}
    for row in csv.reader(csv_file, delimiter=';'):
        if not header_row:
            header_row = row
            continue
        row = dict(zip(header_row, row))
        photos_metadata[row.get('number')] = row
    zip_file = zipfile.ZipFile(request.FILES['zip_file'])
    album_id = request.POST.get('album_id')
    album = Album.objects.get(pk=album_id)
    licence = Licence.objects.get(name='Public domain')
    for key, value in photos_metadata.items():
        try:
            image_file = zip_file.read(value['filename'])
        except KeyError:
            continue
        meta_for_this_image = photos_metadata[key]
        source_name = meta_for_this_image.get('institution') or 'Ajapaik'
        try:
            source = Source.objects.get(description=source_name)
        except ObjectDoesNotExist:
            source = Source(name=source_name, description=source_name)
            source.save()
        # FIXME: Maybe we want to re-upload? Can't just skip
        try:
            Photo.objects.get(source=source, source_key=key)
            continue
        except ObjectDoesNotExist:
            pass
        extension = 'jpeg'
        upload_file_name = 'uploads/%s.%s' % (hashlib.md5(key).hexdigest(), extension)
        fout = open('/var/garage/' + upload_file_name, 'w')
        fout.write(image_file)
        fout.close()
        place_name = meta_for_this_image.get('place') or 'Ajapaik'
        try:
            area = Area.objects.get(name=place_name)
        except ObjectDoesNotExist:
            area = Area(name=place_name)
            area.save()
        description = '; '.join(filter(None, [meta_for_this_image[sub_key].strip() for sub_key
                                              in ('description', 'title') if sub_key in meta_for_this_image]))
        description = description.strip(' \t\n\r')
        source_url = meta_for_this_image.get('url')
        p = Photo(
            area=area,
            licence=licence,
            date_text=meta_for_this_image.get('date'),
            description=description,
            source=source,
            source_url=source_url,
            source_key=key,
            author=meta_for_this_image.get('author')
        )
        p.image.name = upload_file_name
        # FIXME: Next 2 lines should happen automatically
        p.width = p.image.width
        p.height = p.image.height
        p.save()
        AlbumPhoto(album=album, photo=p, profile=profile).save()
    album.save()

    return HttpResponse('OK')


@user_passes_test(lambda u: u.groups.filter(name='csv_uploaders').count() == 1, login_url='/admin/')
def norwegian_csv_upload(request):
    import csv
    import hashlib
    profile = request.get_user().profile
    csv_file = request.FILES['csv_file']
    header_row = None
    photos_metadata = {}
    for row in csv.reader(csv_file, delimiter=','):
        if not header_row:
            header_row = row
            continue
        row = dict(zip(header_row, row))
        photos_metadata[row.get('source_number')] = row
    album_id = request.POST.get('album_id')
    album = Album.objects.get(pk=album_id)
    licence = Licence.objects.get(name='Attribution 4.0 International')
    failed = []
    for key, value in photos_metadata.items():
        meta_for_this_image = photos_metadata[key]
        response = requests.get(meta_for_this_image.get('image_url'), stream=True)
        source_name = meta_for_this_image.get('institution') or 'Ajapaik'
        try:
            source = Source.objects.get(description=source_name)
        except ObjectDoesNotExist:
            source = Source(name=source_name, description=source_name)
            source.save()
        # FIXME: Maybe we want to re-upload? Can't just skip
        try:
            Photo.objects.get(source=source, source_key=key.split('.')[0])
            continue
        except ObjectDoesNotExist:
            pass
        extension = 'jpg'
        upload_file_name = 'uploads/%s.%s' % (
            unicode(datetime.datetime.now()) + '_' + hashlib.md5(key).hexdigest(), extension)
        fout = open('/var/garage/' + upload_file_name, 'w')
        shutil.copyfileobj(response.raw, fout)
        fout.close()
        place_name = meta_for_this_image.get('place') or 'Ajapaik'
        try:
            area = Area.objects.get(name=place_name)
        except ObjectDoesNotExist:
            area = Area(name=place_name)
            area.save()
        description = meta_for_this_image.get('title')
        description = description.strip(' \t\n\r')
        source_url = meta_for_this_image.get('source_url')
        p = Photo(
            area=area,
            licence=licence,
            description_no=description,
            source=source,
            source_url=source_url,
            source_key=key.split('.')[0],
            date_text=meta_for_this_image.get('date'),
            author=meta_for_this_image.get('author')
        )
        p.image.name = upload_file_name
        # FIXME: Next 2 lines should happen automatically
        try:
            p.width = p.image.width
            p.height = p.image.height
        except:
            failed.append(key)
            continue
        p.save()
        AlbumPhoto(album=album, photo=p, profile=profile).save()
        if meta_for_this_image.get('lat') and meta_for_this_image.get('lon'):
            source_geotag = GeoTag(
                lat=meta_for_this_image.get('lat'),
                lon=meta_for_this_image.get('lon'),
                origin=GeoTag.SOURCE,
                type=GeoTag.SOURCE_GEOTAG,
                map_type=GeoTag.NO_MAP,
                photo=p,
                is_correct=True,
                trustworthiness=0.07
            )
            source_geotag.save()
            p.latest_geotag = source_geotag.created
        p.set_calculated_fields()
        p.save()
    album.save()

    return HttpResponse(failed)


def newsletter(request, slug=None):
    ret = {
        'is_newsletter': True,
        'ajapaik_facebook_link': settings.AJAPAIK_FACEBOOK_LINK
    }
    if slug:
        ret['newsletter'] = Newsletter.objects.get(slug=slug)
        ret['template'] = 'newsletters/' + ret['newsletter'].slug + '.html'
    else:
        ret['newsletters'] = Newsletter.objects.order_by('created')

    return render_to_response('newsletter.html', RequestContext(request, ret))


def submit_dating(request):
    profile = request.get_user().profile
    form = DatingSubmitForm(request.POST.copy())
    confirm_form = DatingConfirmForm(request.POST)
    form.data['profile'] = profile.id
    if form.is_valid():
        dating = form.save(commit=False)
        if not dating.start:
            dating.start = datetime.datetime.strptime('01011000', '%d%m%Y').date()
        if not dating.end:
            dating.end = datetime.datetime.strptime('01013000', '%d%m%Y').date()
        p = form.cleaned_data['photo']
        dating_exists = Dating.objects.filter(profile=profile, raw=dating.raw, photo=p).exists()
        if not dating_exists:
            dating.save()
            p.latest_dating = dating.created
            if not p.first_dating:
                p.first_dating = dating.created
            confirmation_count = 0
            for each in p.datings.all():
                confirmation_count += each.confirmations.count()
            p.dating_count = p.datings.count() + confirmation_count
            p.light_save()
            Points(
                user=profile,
                action=Points.DATING,
                photo=form.cleaned_data['photo'],
                dating=dating,
                points=DATING_POINTS,
                created=dating.created
            ).save()
            return HttpResponse('OK')
        return HttpResponse('Dating exists', status=400)
    elif confirm_form.is_valid():
        original_dating = confirm_form.cleaned_data['id']
        confirmation_exists = DatingConfirmation.objects.filter(confirmation_of=original_dating,
                                                                profile=profile).exists()
        if not confirmation_exists and original_dating.profile != profile:
            new_confirmation = DatingConfirmation(
                confirmation_of=original_dating,
                profile=profile
            )
            new_confirmation.save()
            p = original_dating.photo
            p.latest_dating = new_confirmation.created
            confirmation_count = 0
            for each in p.datings.all():
                confirmation_count += each.confirmations.count()
            p.dating_count = p.datings.count() + confirmation_count
            p.light_save()
            Points(
                user=profile,
                action=Points.DATING_CONFIRMATION,
                dating_confirmation=new_confirmation,
                points=DATING_CONFIRMATION_POINTS,
                photo=p,
                created=new_confirmation.created
            ).save()
            return HttpResponse('OK')
        else:
            return HttpResponse('Already confirmed or confirming your own dating', status=400)
    else:
        return HttpResponse('Invalid data', status=400)


def get_datings(request, photo_id):
    photo = Photo.objects.filter(pk=photo_id).first()
    profile = request.get_user().profile
    ret = {}
    if photo:
        datings = photo.datings.order_by('created').prefetch_related('confirmations')
        for each in datings:
            each.this_user_has_confirmed = each.confirmations.filter(profile=profile).exists()
        datings_serialized = DatingSerializer(datings, many=True).data
        ret['datings'] = datings_serialized

    return HttpResponse(json.dumps(ret), content_type='application/json')


def generate_still_from_video(request):
    profile = request.get_user().profile
    form = VideoStillCaptureForm(request.POST)
    ret = {}
    if form.is_valid():
        a = form.cleaned_data['album']
        vid = form.cleaned_data['video']
        time = form.cleaned_data['timestamp']
        still = Photo.objects.filter(video=vid, video_timestamp=time).first()
        if not still:
            vidcap = cv2.VideoCapture(vid.file.path)
            vidcap.set(0, time)
            success, image = vidcap.read()
            source = Source.objects.filter(name='AJP').first()
            if success:
                tmp = NamedTemporaryFile(suffix='.jpeg', delete=True)
                cv2.imwrite(tmp.name, image)
                hours, milliseconds = divmod(time, 3600000)
                minutes, milliseconds = divmod(time, 60000)
                seconds = float(milliseconds) / 1000
                s = "%i:%02i:%06.3f" % (hours, minutes, seconds)
                description = _('Still from "%(film)s" at %(time)s') % {'film': vid.name, 'time': s}
                still = Photo(
                    description=description,
                    user=profile,
                    types='film,still,frame,snapshot,filmi,kaader,pilt',
                    video=vid,
                    video_timestamp=time,
                    source=source
                )
                still.save()
                still.source_key = still.id
                still.source_url = request.build_absolute_uri(
                    reverse('project.ajapaik.views.photoslug', args=(still.id, still.get_pseudo_slug())))
                still.image.save(unicodedata.normalize('NFKD', description).encode('ascii', 'ignore') + '.jpeg',
                                 File(tmp))
                still.light_save()
                AlbumPhoto(album=a, photo=still, profile=profile, type=AlbumPhoto.STILL).save()
                Points(
                    user=profile,
                    action=Points.FILM_STILL,
                    photo=still,
                    album=a,
                    points=50,
                    created=still.created
                ).save()
                a.set_calculated_fields()
                a.save()
        ret['stillId'] = still.id

    return HttpResponse(json.dumps(ret), content_type='application/json')


# to_hex = lambda x: ''.join([hex(ord(c))[2:].zfill(2) for c in x])
#
# def maksekeskus_payment(request):
#     if request.method == 'POST':
#         form = DonationAmountForm(request.POST)
#         if form.is_valid():
#             json_str = json.dumps({
#                 'shop': '123',
#                 'amount': form.cleaned_data['amount']
#             })
#             redirect_form = DonationForm(initial={
#                 'json': json_str,
#                 'mac': str(to_hex(hashlib.sha1((json_str + MAKSEKESKUS_SECRET).encode('utf-8')).digest())).upper()
#             })
#             return render_to_response('maksekeskus_redirect.html', RequestContext(request, {'form': redirect_form}))
#
#     return redirect('/')

def donate(request):
    ret = {
        'is_donate': True
    }
    return render_to_response('donate.html', RequestContext(request, ret))


def photo_upload_choice(request):
    if request.method == 'POST':
        form = PhotoUploadChoiceForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['action'] == 'import':
                return redirect('curator')
            else:
                return redirect('user_upload')
    else:
        form = PhotoUploadChoiceForm()
    ret = {
        'form': form,
        'is_upload_choice': True
    }

    return render_to_response('photo_upload_choice.html', RequestContext(request, ret))


@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/?next=user-upload')
def user_upload(request):
    ret = {}
    if request.method == 'POST':
        form = UserPhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.user = request.user.profile
            if photo.uploader_is_author:
                photo.author = request.user.profile.get_display_name()
                photo.licence = Licence.objects.filter(url='https://creativecommons.org/licenses/by-sa/4.0/').first()
            photo.save()
            for each in form.cleaned_data['albums']:
                AlbumPhoto(
                    photo=photo,
                    album=each,
                    type=AlbumPhoto.UPLOADED,
                    profile=request.user.profile
                ).save()
            form = UserPhotoUploadForm()
            if request.POST.get('geotag') == 'true':
                return redirect(reverse('frontpage_photos') + '?photo=' + str(photo.id) + '&locationToolsOpen=1')
            else:
                ret['message'] = _('Photo uploaded')
    else:
        form = UserPhotoUploadForm()
    ret['form'] = form

    return render_to_response('user_upload.html', RequestContext(request, ret))


@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/?next=user-upload-add-album')
def user_upload_add_album(request):
    ret = {}
    if request.method == 'POST':
        form = UserPhotoUploadAddAlbumForm(request.POST, profile=request.user.profile)
        if form.is_valid():
            album = form.save(commit=False)
            album.atype = Album.CURATED
            album.profile = request.user.profile
            album.save()
            ret['message'] = _('Album created')
    else:
        form = UserPhotoUploadAddAlbumForm(profile=request.user.profile)
    ret['form'] = form

    return render_to_response('user_upload_add_album.html', RequestContext(request, ret))


def perform_delete(request, comment):
    flag, created = CommentFlag.objects.get_or_create(
        comment_id=comment.pk,
        user=request.user,
        flag=CommentFlag.MODERATOR_DELETION
    )
    comment.is_removed = True
    comment.save()
    comment_was_flagged.send(
        sender=comment.__class__,
        comment=comment,
        flag=flag,
        created=created,
        request=request,
    )


@csrf_protect
def delete_comment(request, comment_id):
    comment = get_object_or_404(django_comments.get_model(), pk=comment_id, site__pk=settings.SITE_ID,
                                user=request.user)
    if request.method == 'POST' and comment:
        perform_delete(request, comment)

        return next_redirect(request, fallback='comments-delete-done', c=comment.pk)
    else:
        return render(request, 'comments/delete.html', {'comment': comment, "next": request.GET["next"]})


# TODO: Should just use 1 info URL to save requests
def get_comment_like_count(request, comment_id):
    comment = get_object_or_404(django_comments.get_model(), pk=comment_id, site__pk=settings.SITE_ID)

    return JsonResponse({'count': comment.like_count()})


def get_comment_dislike_count(request, comment_id):
    comment = get_object_or_404(django_comments.get_model(), pk=comment_id, site__pk=settings.SITE_ID)

    return JsonResponse({'count': comment.dislike_count()})


def privacy(request):
    return render_to_response('privacy.html', RequestContext(request, {}))


def terms(request):
    return render_to_response('terms.html', RequestContext(request, {}))
