# encoding: utf-8
import hashlib
import os
import urllib2
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.gis.measure import D
from django.core.urlresolvers import reverse
from django.db.models import Sum, Q, Count

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.sites.models import Site
from django.http import HttpResponse

from django.utils.translation import ugettext as _
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.gis.geos import Polygon, Point
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
import requests
from rest_framework.renderers import JSONRenderer

from project.home.models import Photo, Profile, Source, Device, DifficultyFeedback, GeoTag, FlipFeedback, UserMapView, Points, \
    Album, AlbumPhoto, Area, Licence, distance_in_meters, _angle_diff, Skip
from project.home.forms import AddAlbumForm, PublicPhotoUploadForm, AreaSelectionForm, AlbumSelectionForm, AddAreaForm, \
    CuratorPhotoUploadForm, GameAlbumSelectionForm, CuratorAlbumSelectionForm, CuratorAlbumEditForm, SubmitGeotagForm
from sorl.thumbnail import get_thumbnail
from PIL import Image, ImageFile
from project.home.serializers import CuratorAlbumSelectionAlbumSerializer, CuratorMyAlbumListAlbumSerializer, \
    CuratorAlbumInfoSerializer

ImageFile.LOAD_TRUNCATED_IMAGES = True
from PIL.ExifTags import TAGS, GPSTAGS
from time import strftime, strptime

import get_next_photos_to_geotag
import random
import datetime
import json
import PIL.ImageOps

from europeana import Search, BoundingBox

def _convert_to_degress(value):
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)

    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)

    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)


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
                exif_data[str(decoded) + '.' + str(sub_decoded)] = value[t]
        elif len(str(value)) < 50:
            exif_data[decoded] = value
        else:
            exif_data[decoded] = None

    return exif_data


def _extract_and_save_data_from_exif(photo_with_exif):
    img = Image.open(settings.MEDIA_ROOT + "/" + str(photo_with_exif.image))
    exif_data = _get_exif_data(img)
    if exif_data:
        if 'GPSInfo.GPSLatitudeRef' in exif_data and 'GPSInfo.GPSLatitude' in exif_data and 'GPSInfo.GPSLongitudeRef' in exif_data and 'GPSInfo.GPSLongitude' in exif_data:
            gps_latitude_ref = exif_data.get('GPSInfo.GPSLatitudeRef')
            gps_latitude = exif_data.get('GPSInfo.GPSLatitude')
            gps_longitude_ref = exif_data.get('GPSInfo.GPSLongitudeRef')
            gps_longitude = exif_data.get('GPSInfo.GPSLongitude')
            lat = _convert_to_degress(gps_latitude)
            if gps_latitude_ref != "N":
                lat = 0 - lat
            lon = _convert_to_degress(gps_longitude)
            if gps_longitude_ref != "E":
                lon = 0 - lon
            photo_with_exif.lat = lat
            photo_with_exif.lon = lon
            photo_with_exif.save()
        if 'Make' in exif_data or 'Model' in exif_data or 'LensMake' in exif_data or 'LensModel' in exif_data or 'Software' in exif_data:
            camera_make = exif_data.get('Make')
            camera_model = exif_data.get('Model')
            lens_make = exif_data.get('LensMake')
            lens_model = exif_data.get('LensModel')
            software = exif_data.get('Software')
            try:
                device = Device.objects.get(camera_make=camera_make, camera_model=camera_model, lens_make=lens_make, lens_model=lens_model, software=software)
            except ObjectDoesNotExist:
                try:
                    device = Device(camera_make=camera_make, camera_model=camera_model, lens_make=lens_make, lens_model=lens_model, software=software)
                    device.save()
                except:
                    device = None
            photo_with_exif.device = device
            photo_with_exif.save()
        if 'DateTimeOriginal' in exif_data and not photo_with_exif.date:
            date_taken = exif_data.get('DateTimeOriginal')
            try:
                parsed_time = strptime(date_taken, "%Y:%m:%d %H:%M:%S")
            except ValueError:
                parsed_time = None
            if parsed_time:
                parsed_time = strftime("%H:%M:%S", parsed_time)
            # ignore default camera dates
            if parsed_time and parsed_time != '12:00:00' and parsed_time != '00:00:00':
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


def handle_uploaded_file(f):
    return ContentFile(f.read())


@csrf_exempt
def photo_upload(request, photo_id):
    photo = get_object_or_404(Photo, pk=photo_id)
    new_id = 0

    if request.method == 'POST':
        profile = request.get_user().profile
        if 'fb_access_token' in request.POST:
            token = request.POST.get('fb_access_token')
            profile, fb_data = Profile.facebook.get_user(token)
            if profile is None:
                user = request.get_user()
                profile = user.profile
                profile.update_from_fb_data(token, fb_data)
        if 'user_file[]' in request.FILES.keys():
            for f in request.FILES.getlist('user_file[]'):
                fileobj = handle_uploaded_file(f)
                data = request.POST
                date_taken = data.get('dateTaken', None)
                re_photo = Photo(
                    rephoto_of=photo,
                    area=photo.area,
                    licence=Licence.objects.get(name='Attribution-ShareAlike 4.0 International'),
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
                        parsed_date_taken = strptime(date_taken, "%d.%m.%Y %H:%M")
                        re_photo.date = strftime("%Y-%m-%d %H:%M", parsed_date_taken)
                    except:
                        pass
                if re_photo.cam_scale_factor:
                    re_photo.cam_scale_factor = round(float(re_photo.cam_scale_factor), 6)
                re_photo.save()
                re_photo.image.save(f.name, fileobj)
                new_id = re_photo.pk

                img = Image.open(settings.MEDIA_ROOT + "/" + str(re_photo.image))
                _extract_and_save_data_from_exif(re_photo)

                # if re_photo.cam_scale_factor:
                #     new_size = tuple([int(x * re_photo.cam_scale_factor) for x in img.size])
                #     output_file = StringIO()
                #
                #     if re_photo.cam_scale_factor < 1:
                #         x0 = (img.size[0] - new_size[0]) / 2
                #         y0 = (img.size[1] - new_size[1]) / 2
                #         x1 = img.size[0] - x0
                #         y1 = img.size[1] - y0
                #         new_img = img.transform(new_size, Image.EXTENT, (x0, y0, x1, y1))
                #         new_img.save(output_file, 'JPEG', quality=95)
                #         re_photo.image_unscaled = deepcopy(re_photo.image)
                #         new_name = str(re_photo.image).split('.')[0] + str(datetime.datetime.now().microsecond) + str(re_photo.image).split('.')[1]
                #         re_photo.image_unscaled.save(new_name, ContentFile(img))
                #         re_photo.image.save(str(re_photo.image), ContentFile(output_file.getvalue()))
                #     elif re_photo.cam_scale_factor > 1:
                #         x0 = (new_size[0] - img.size[0]) / 2
                #         y0 = (new_size[1] - img.size[1]) / 2
                #         new_img = Image.new("RGB", new_size)
                #         new_img.paste(img, (x0, y0))
                #         new_img.save(output_file, 'JPEG', quality=95)
                #         re_photo.image_unscaled = deepcopy(re_photo.image)
                #         new_name = str(re_photo.image).split('.')[0] + str(datetime.datetime.now().microsecond) + str(re_photo.image).split('.')[1]
                #         re_photo.image_unscaled.save(new_name, ContentFile(img))
                #         re_photo.image.save(str(re_photo.image), ContentFile(output_file.getvalue()))

        profile.update_rephoto_score()

    return HttpResponse(json.dumps({'new_id': new_id}), content_type="application/json")


def logout(request):
    from django.contrib.auth import logout

    logout(request)

    if 'HTTP_REFERER' in request.META:
        return redirect(request.META['HTTP_REFERER'])

    return redirect('/')


def calculate_recent_activity_scores():
    five_thousand_actions_ago = Points.objects.order_by('-created')[5000].created
    recent_actions = Points.objects.filter(created__gt=five_thousand_actions_ago).values('user_id').annotate(total_points=Sum('points'))
    recent_action_agent_ids = []
    for each in recent_actions:
        profile = Profile.objects.filter(user_id=each['user_id']).get()
        recent_action_agent_ids.append(profile.id)
        profile.score_recent_activity = each['total_points']
        profile.save()
    # Check for people who somehow no longer have actions among the last 1000
    orphan_profiles = Profile.objects.filter(score_recent_activity__gt=0).exclude(pk__in=recent_action_agent_ids)
    for each in orphan_profiles:
        each.score_recent_activity = 0
        each.save()


@ensure_csrf_cookie
def game(request):
    ctx = {}
    area_selection_form = AreaSelectionForm(request.GET)
    album_selection_form = AlbumSelectionForm(request.GET)
    game_album_selection_form = GameAlbumSelectionForm(request.GET)

    if game_album_selection_form.is_valid():
        # FIXME: Way too many queries
        album = game_album_selection_form.cleaned_data['album']
        ctx['album'] = album
        album_photo_ids = album.photos.values_list('id', flat=True)
        ctx['total_photo_count'] = album.photos.distinct('id').count()
        ctx['geotagged_photo_count'] = album.photos.filter(
            rephoto_of__isnull=True, lat__isnull=False, lon__isnull=False).distinct('id').count()
        ctx['user_geotagged_photo_count'] = GeoTag.objects.filter(
            user=request.get_user().profile, photo_id__in=album_photo_ids).distinct('photo_id').count()
        ctx['geotagging_user_count'] = GeoTag.objects.filter(photo_id__in=album_photo_ids).distinct('user').count()
        ctx['rephoto_user_count'] = Photo.objects.filter(rephoto_of_id__in=album_photo_ids).distinct('user').count()
        ctx['rephoto_count'] = Photo.objects.filter(rephoto_of_id__in=album_photo_ids).count()
        ctx['rephotographed_photo_count'] = Photo.objects.filter(rephoto_of_id__in=album_photo_ids)\
            .distinct('rephoto_of').count()
        ctx['user_rephoto_count'] = Photo.objects.filter(
            rephoto_of_id__in=album_photo_ids, user=request.get_user().profile).count()
        ctx['user_rephotographed_photo_count'] = Photo.objects.filter(
            rephoto_of_id__in=album_photo_ids, user=request.get_user().profile).distinct('rephoto_of').count()
        if album.geography:
            ctx['nearby_albums'] = Album.objects.filter(geography__distance_lte=(
                Point(album.lat, album.lon), D(m=50000)), is_public=True).exclude(id__in=[album.id])[:3]
        ctx['description'] = album.name
        ctx['share_link'] = request.build_absolute_uri(reverse('project.home.views.game'))
        ctx['facebook_share_photos'] = album.photos.all()[:5]
        try:
            ctx['random_album_photo'] = album.photos.filter(lat__isnull=False, lon__isnull=False).order_by('?')[0]
        except:
            try:
                ctx['random_album_photo'] = album.photos.filter(area__isnull=False).order_by('?')[0]
            except:
                pass
    else:
        if area_selection_form.is_valid():
            area = area_selection_form.cleaned_data['area']
        else:
            old_city_id = request.GET.get('city__pk') or None
            if old_city_id is not None:
                area = Area.objects.get(pk=old_city_id)
            else:
                area = Area.objects.get(pk=settings.DEFAULT_AREA_ID)
        ctx['area'] = area

    site = Site.objects.get_current()
    ctx['hostname'] = 'http://%s' % (site.domain, )
    ctx['title'] = _("Let's put pictures on the map")
    ctx['is_game'] = True
    ctx['area_selection_form'] = area_selection_form
    ctx['album_selection_form'] = album_selection_form

    return render_to_response('game.html', RequestContext(request, ctx))


def frontpage(request):
    try:
        example = random.choice(Photo.objects.filter(
            id__in=[2483, 2495, 2502, 3193, 3195, 3201, 3203, 3307, 4821, 5485, 5535, 5588, 5617, 5644, 5645, 5646],
            rephoto_of__isnull=False))
    except ObjectDoesNotExist:
        example = random.choice(Photo.objects.filter(rephoto_of__isnull=False)[:8])
    example_source = Photo.objects.get(pk=example.rephoto_of.id)
    album_selection_form = AlbumSelectionForm(request.GET)

    if not album_selection_form.is_valid():
        album_selection_form = AlbumSelectionForm()

    return render_to_response('frontpage.html', RequestContext(request, {
        'album_selection_form': album_selection_form,
        'example': example,
        'example_source': example_source,
        'grid_view_enabled': settings.GRID_VIEW_ENABLED,
        'photo_upload_enabled': settings.PUBLIC_PHOTO_UPLOAD_ENABLED,
        'curator_enabled': settings.CURATOR_ENABLED,
    }))


def photo_large(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    if photo.cam_scale_factor and photo.rephoto_of:
        # if rephoto is taken with mobile then make it same width/height as source photo
        im = get_thumbnail(photo.rephoto_of.image, '1024x1024', upscale=False)
        im = get_thumbnail(photo.image, str(im.width) + 'x' + str(im.height), crop="center")
    else:
        im = get_thumbnail(photo.image, '1024x1024', upscale=False)
    content = im.read()
    next_week = datetime.datetime.now() + datetime.timedelta(seconds=604800)
    response = HttpResponse(content, content_type='image/jpg')
    response['Content-Length'] = len(content)
    response['Cache-Control'] = "max-age=604800, public"  # 604800 = 7 days
    response['Expires'] = next_week.strftime("%a, %d %b %y %T GMT")
    return response


def photo_url(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    if (photo.cam_scale_factor and photo.rephoto_of):
        # if rephoto is taken with mobile then make it same width/height as source photo
        im = get_thumbnail(photo.rephoto_of.image, '700x400')
        im = get_thumbnail(photo.image, str(im.width) + 'x' + str(im.height), crop="center")
    else:
        im = get_thumbnail(photo.image, '700x400')
    content = im.read()
    next_week = datetime.datetime.now() + datetime.timedelta(seconds=604800)
    response = HttpResponse(content, content_type='image/jpg')
    response['Content-Length'] = len(content)
    response['Cache-Control'] = "max-age=604800, public"  # 604800 = 7 days
    response['Expires'] = next_week.strftime("%a, %d %b %y %T GMT")
    return response


def photo_thumb(request, photo_id, thumb_size=150):
    cache_key = "ajapaik_pane_photo_thumb_response_%s_%s" % (photo_id, thumb_size)
    cached_response = cache.get(cache_key)
    if cached_response:
        return cached_response
    p = get_object_or_404(Photo, id=photo_id)
    if p.image_unscaled:
        try:
            if os.path.exists(p.image_unscaled.file.name):
                image_to_use = p.image_unscaled
        except ValueError:
            image_to_use = p.image
    else:
        image_to_use = p.image
    thumb_str = str(thumb_size) + 'x' + str(thumb_size)
    im = get_thumbnail(image_to_use, thumb_str, upscale=False)
    content = im.read()
    next_week = datetime.datetime.now() + datetime.timedelta(seconds=604800)
    response = HttpResponse(content, content_type='image/jpg')
    response['Content-Length'] = len(content)
    response['Cache-Control'] = "max-age=604800, public"
    response['Expires'] = next_week.strftime("%a, %d %b %y %T GMT")
    cache.set(cache_key, response)
    return response


def photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    pseudo_slug = photo.get_pseudo_slug()
    # slug not needed if not enough data for slug or ajax request
    if pseudo_slug != "" and not request.is_ajax():
        return photoslug(request, photo.id, "")
    else:
        return photoslug(request, photo.id, pseudo_slug)


def _add_log_entry_if_necessary(user_profile, photo_id, user_action):
    existing_log_entry = None
    try:
        existing_log_entry = UserMapView.objects.filter(user_profile=user_profile, photo_id=photo_id,
                                                        action=user_action)[:1].get()
    except ObjectDoesNotExist:
        if photo_id and user_action and not existing_log_entry:
            target_photo = Photo.objects.filter(id=photo_id)[:1].get()
            log_entry = UserMapView()
            log_entry.photo_id = photo_id
            log_entry.confidence = target_photo.confidence
            log_entry.action = user_action
            log_entry.user_profile = user_profile
            log_entry.save()


def heatmap_data(request):
    res = {}
    photo_id = request.GET.get("photo_id") or None
    if photo_id:
        target_photo = Photo.objects.filter(pk=photo_id).get()
        if hasattr(target_photo, "rephoto_of") and target_photo.rephoto_of is not None:
            target_photo = target_photo.rephoto_of
        if target_photo.lat and target_photo.lon:
            res["estimated_location"] = [target_photo.lat, target_photo.lon]
        res["confidence"] = target_photo.confidence
        res["heatmap_points"] = target_photo.get_heatmap_points()
        res["azimuth_tags"] = 0
        for point in res["heatmap_points"]:
            if point[2]:
                res["azimuth_tags"] += 1
    return HttpResponse(json.dumps(res), content_type="application/json")

def _make_fullscreen(photo):
    if photo:
        image = get_thumbnail(photo.image, '1024x1024', upscale=False)
        return {'url': image.url, 'size': [image.width, image.height]}

def photoslug(request, photo_id, pseudo_slug):
    photo_obj = get_object_or_404(Photo, id=photo_id)
    user_profile = request.get_user().profile
    _add_log_entry_if_necessary(user_profile, photo_id, "opened_drawer")
    # redirect if slug in url doesn't match with our pseudo slug
    if photo_obj.get_pseudo_slug() != pseudo_slug:
        response = HttpResponse(content="", status=301)  # HTTP 301 for google juice
        response["Location"] = photo_obj.get_absolute_url()
        return response

    # switch places if rephoto url
    rephoto = None
    if hasattr(photo_obj, 'rephoto_of') and photo_obj.rephoto_of is not None:
        rephoto = photo_obj
        photo_obj = photo_obj.rephoto_of

    if photo_obj:
        geotag_count = GeoTag.objects.filter(photo_id=photo_obj.id).count()
        azimuth_count = GeoTag.objects.filter(photo_id=photo_obj.id, azimuth__isnull=False).count()

    site = Site.objects.get_current()
    template = ['', '_photo_modal.html', 'photoview.html'][request.is_ajax() and 1 or 2]
    if not photo_obj.description:
        title = "Unknown photo"
    else:
        title = ' '.join(photo_obj.description.split(' ')[:5])[:50]

    album = None
    try:
        album_ids = AlbumPhoto.objects.filter(photo_id=photo_obj.id).values_list('album_id', flat=True)
        albums = Album.objects.filter(pk__in=album_ids, is_public=True)
        album = albums[0]
        album_selection_form = AlbumSelectionForm({'album': album.id})
    except:
        album_selection_form = AlbumSelectionForm()

    #if photo_obj.area:
        #area_selection_form = AreaSelectionForm({'area': photo_obj.area.id})

    return render_to_response(template, RequestContext(request, {
        'photo': photo_obj,
        'licence': Licence.objects.get(name="Attribution-ShareAlike 4.0 International"),
        'area': photo_obj.area,
        'album': album,
        'album_selection_form': album_selection_form,
        'geotag_count': geotag_count,
        'azimuth_count': azimuth_count,
        #'area_selection_form': area_selection_form,
        'fullscreen': _make_fullscreen(photo_obj),
        'rephoto_fullscreen': _make_fullscreen(rephoto),
        'title': title,
        'description': photo_obj.description.rstrip(),
        'rephoto': rephoto,
        'hostname': 'http://%s' % (site.domain, ),
        'is_photoview': True
    }))


@ensure_csrf_cookie
def mapview(request, photo_id=None, rephoto_id=None):
    area_selection_form = AreaSelectionForm(request.GET)
    album_selection_form = AlbumSelectionForm(request.GET)
    game_album_selection_form = GameAlbumSelectionForm(request.GET)
    area = None
    album = None

    if area_selection_form.is_valid():
        area = Area.objects.get(pk=area_selection_form.cleaned_data['area'].id)

    if game_album_selection_form.is_valid():
        album = Album.objects.get(pk=game_album_selection_form.cleaned_data['album'].id)

    selected_rephoto = None
    if rephoto_id:
        try:
            selected_rephoto = Photo.objects.get(pk=rephoto_id, rephoto_of__isnull=False)
        except ObjectDoesNotExist:
            pass

    selected_photo = None
    if photo_id:
        try:
            selected_photo = Photo.objects.get(pk=photo_id)
        except ObjectDoesNotExist:
            pass
    else:
        if selected_rephoto:
            try:
                selected_photo = Photo.objects.get(pk=selected_rephoto.rephoto_of.id)
            except ObjectDoesNotExist:
                pass

    if selected_photo and area is None:
        try:
            area = Area.objects.get(pk=selected_photo.area_id)
        except ObjectDoesNotExist:
            pass

    random_album_photo = None
    if album is not None:
        title = album.name + ' - ' + _('Browse photos on map')
        try:
            random_album_photo = album.photos.filter(lat__isnull=False, lon__isnull=False).order_by('?')[0]
        except:
            try:
                random_album_photo = album.photos.filter(area__isnull=False).order_by('?')[0]
            except:
                pass
    elif area is not None:
        title = area.name + ' - ' + _('Browse photos on map')
    else:
        title = _('Browse photos on map')

    return render_to_response('mapview.html', RequestContext(request, {
        'area': area,
        'album': album,
        'title': title,
        'album_selection_form': album_selection_form,
        'random_album_photo': random_album_photo,
        'selected_photo': selected_photo,
        'selected_rephoto': selected_rephoto,
        'is_mapview': True
    }))


def map_objects_by_bounding_box(request):
    data = request.POST

    album_id = data.get('album_id') or None
    area_id = data.get('area_id') or None
    limit_by_album = data.get('limit_by_album') or None

    if limit_by_album == 'true':
        limit_by_album = True
    else:
        limit_by_album = False

    qs = Photo.objects.all()

    ungeotagged_count = 0
    geotagged_count = 0
    if album_id is not None or area_id is not None:
        ungeotagged_count, geotagged_count = qs.get_album_photo_count_and_total_geotag_count(album_id, area_id)
        if album_id and limit_by_album:
            album = Album.objects.get(pk=album_id)
            album_photo_ids = list(album.photos.values_list('id', flat=True))
            #subalbums = album.subalbums.filter(is_public=True).all()
            subalbums = album.subalbums.all()
            for sa in subalbums:
                album_photo_ids += sa.photos.values_list('id', flat=True)
            qs = qs.filter(id__in=album_photo_ids)

    if data.get('sw_lat') and data.get('sw_lon') and data.get('ne_lat') and data.get('ne_lon'):
        bounding_box = (float(data.get('sw_lat')), float(data.get('sw_lon')), float(data.get('ne_lat')), float(data.get('ne_lon')))
        data = qs.get_geotagged_photos_list(bounding_box)
        data = {'photos': data, 'geotagged_count': geotagged_count, 'ungeotagged_count': ungeotagged_count}
    else:
        data = {'photos': [], 'geotagged_count': 0, 'ungeotagged_count': 0}

    return HttpResponse(json.dumps(data), content_type="application/json")


def get_leaderboard(request):
    return HttpResponse(json.dumps(get_next_photos_to_geotag.get_leaderboard(request.get_user().profile.pk)), content_type="application/json")


@login_required
def geotag_add(request):
    submit_geotag_form = SubmitGeotagForm(request.POST)
    profile = request.get_user().profile
    ret = {
        'location_correct': False,
        'this_guess_score': 0
    }
    if submit_geotag_form.is_valid():
        azimuth_score = 0
        new_geotag = submit_geotag_form.save(commit=False)
        new_geotag.user = profile
        trust = get_next_photos_to_geotag.calc_trustworthiness(profile.id)
        new_geotag.trustworthiness = trust
        new_geotag.save()
        tagged_photo = submit_geotag_form.cleaned_data['photo']
        tagged_photo.set_calculated_fields()
        tagged_photo.save()
        processed_tagged_photo = Photo.objects.filter(pk=tagged_photo.id).get()
        ret['estimated_location'] = [processed_tagged_photo.lat, processed_tagged_photo.lon]
        processed_geotag = GeoTag.objects.filter(pk=new_geotag.id).get()
        if processed_geotag.origin == GeoTag.GAME:
            if len(tagged_photo.geotags.all()) == 1:
                score = max(20, int(300 * trust))
            else:
                error_in_meters = distance_in_meters(tagged_photo.lon, tagged_photo.lat, processed_geotag.lon,
                                                     processed_geotag.lat)
                score = int(130 * max(0, min(1, (1 - (error_in_meters - 15) / float(94 - 15)))))
        else:
            score = int(trust * 100)
        if processed_geotag.hint_used:
            score *= 0.75
        if processed_geotag.azimuth_correct:
            degree_error_point_array = [100, 99, 97, 93, 87, 83, 79, 73, 67, 61, 55, 46, 37, 28, 19, 10]
            difference = int(_angle_diff(tagged_photo.azimuth, processed_geotag.azimuth))
            if difference <= 15:
                azimuth_score = degree_error_point_array[int(difference)]
        processed_geotag.azimuth_score = azimuth_score
        processed_geotag.score = score + azimuth_score
        processed_geotag.save()
        ret['is_correct'] = processed_geotag.is_correct
        ret['current_score'] = processed_geotag.score
        Points(user=profile, action=Points.GEOTAG, geotag=processed_geotag, points=processed_geotag.score,
               created=datetime.datetime.now()).save()
        geotags_for_this_photo = GeoTag.objects.filter(photo=tagged_photo)
        ret['heatmap_points'] = [[x.lat, x.lon] for x in geotags_for_this_photo]
        ret['azimuth_tags'] = geotags_for_this_photo.filter(azimuth__isnull=False).count()
        ret['confidence'] = processed_tagged_photo.confidence
        profile.set_calculated_fields()
        profile.save()
        if processed_geotag.origin == GeoTag.GAME:
            if processed_geotag.is_correct:
                ret['feedback_message'] = _('Looks right!')
                if not processed_geotag.azimuth:
                    ret['feedback_message'] = \
                        _('The location seems right. Try submitting an azimuth to earn even more points!')
                else:
                    if not processed_geotag.azimuth_correct:
                        ret['feedback_message'] = _('The location seems right, but not the azimuth.')
                    if ret['azimuth_tags'] == 1:
                        ret['feedback_message'] = _('The location seems right, your azimuth was first.')
            else:
                ret['feedback_message'] = _("Other users have different opinion.")
            if len(geotags_for_this_photo) == 1:
                ret['feedback_message'] = _('Your guess was first.')
    else:
        if 'lat' not in submit_geotag_form.cleaned_data and 'lon' not in submit_geotag_form.cleaned_data \
                and 'photo_id' in submit_geotag_form.data:
            Skip(user=profile, photo_id=submit_geotag_form.data['photo_id']).save()

    return HttpResponse(json.dumps(ret), content_type="application/json")


def leaderboard(request):
    # leaderboard with first position, one in front of you, your score and one after you
    calculate_recent_activity_scores()
    response = get_next_photos_to_geotag.get_leaderboard(request.get_user().profile.pk)
    template = ['', '_block_leaderboard.html', 'leaderboard.html'][request.is_ajax() and 1 or 2]
    return render_to_response(template, RequestContext(request, {
        'leaderboard': response,
        'title': _('Leaderboard'),
        'is_top_50': False
    }))


def top50(request):
    # leaderboard with top 50 scores
    calculate_recent_activity_scores()
    activity_leaderboard = get_next_photos_to_geotag.get_leaderboard50(request.get_user().profile.pk)
    all_time_leaderboard = get_next_photos_to_geotag.get_all_time_leaderboard50(request.get_user().profile.pk)
    template = ['', '_block_leaderboard.html', 'leaderboard.html'][request.is_ajax() and 1 or 2]
    return render_to_response(template, RequestContext(request, {
        'activity_leaderboard': activity_leaderboard,
        'all_time_leaderboard': all_time_leaderboard,
        'title': _('Leaderboard'),
        'is_top_50': True
    }))


def fetch_stream(request):
    area_selection_form = AreaSelectionForm(request.GET)
    area = None
    if area_selection_form.is_valid():
        area = Area.objects.get(pk=area_selection_form.cleaned_data['area'].id)
    else:
        old_city_id = request.GET.get('city__pk') or None
        if old_city_id is not None:
            area = Area.objects.get(pk=old_city_id)

    game_album_selection_form = GameAlbumSelectionForm(request.GET)
    album = None
    if game_album_selection_form.is_valid():
        album = Album.objects.get(pk=game_album_selection_form.cleaned_data['album'].id)

    qs = Photo.objects.filter()

    if album is not None:
        photos_ids_in_album = list(album.photos.values_list('id', flat=True))
        #subalbums = album.subalbums.filter(is_public=True).all()
        subalbums = album.subalbums.all()
        if len(subalbums) > 0:
            for sa in subalbums:
                photos_ids_in_subalbum = list(sa.photos.values_list('id', flat=True))
                photos_ids_in_album += photos_ids_in_subalbum
        qs = qs.filter(pk__in=photos_ids_in_album)
    else:
        if area is not None:
            qs = qs.filter(area_id=area.id)

    # TODO: [0][0] Wtf?
    try:
        data = {"photo": qs.get_next_photo_to_geotag(request)[0][0], "user_seen_all": qs.get_next_photo_to_geotag(request)[1],
                "nothing_more_to_show": qs.get_next_photo_to_geotag(request)[2]}
    except IndexError:
        data = {"photo": None, "user_seen_all": False, "nothing_more_to_show": False}

    return HttpResponse(json.dumps(data), content_type="application/json")


def difficulty_feedback(request):
    # TODO: Tighten down security when it becomes apparent people are abusing this

    user_profile = request.get_user().profile
    if not user_profile:
        return HttpResponse("Error", status=500)
    user_trustworthiness = get_next_photos_to_geotag.calc_trustworthiness(user_profile.pk)
    user_last_geotag = GeoTag.objects.filter(user=user_profile).order_by("-created")[:1].get()
    level = request.POST.get("level") or None
    photo_id = request.POST.get("photo_id") or None
    if user_profile and level and photo_id:
        feedback_object = DifficultyFeedback()
        feedback_object.user_profile = user_profile
        feedback_object.level = level
        feedback_object.photo_id = photo_id
        feedback_object.trustworthiness = user_trustworthiness
        feedback_object.geotag = user_last_geotag
        feedback_object.save()
    photo = Photo.objects.filter(id=photo_id)[:1].get()
    photo.set_calculated_fields()
    photo.save()
    return HttpResponse("OK")


def log_user_map_action(request):
    user_profile = request.get_user().profile
    photo_id = request.POST.get("photo_id") or None
    user_action = request.POST.get("user_action") or None
    _add_log_entry_if_necessary(user_profile, photo_id, user_action)
    return HttpResponse("OK")


def custom_404(request):
    response = render_to_response('404.html', {}, context_instance=RequestContext(request))
    response.status_code = 404
    return response


def custom_500(request):
    response = render_to_response('500.html', {}, context_instance=RequestContext(request))
    response.status_code = 500
    return response


def europeana(request):
    # This is for testing Europeana integration, nothing good yet
    x1 = request.GET.get("x1", None)
    x2 = request.GET.get("x2", None)
    y1 = request.GET.get("y1", None)
    y2 = request.GET.get("y2", None)
    bounding_box = None
    if x1 and x2 and y1 and y2:
        bounding_box = BoundingBox(float(x1), float(y1), float(x2), float(y2))
    results = Search().query(request.GET.get("query", "Kose"), request.GET.get("refinement_terms", None), bounding_box, request.GET.get("start", 1), request.GET.get("size", 12))
    return render_to_response("europeana.html", RequestContext(request, {
        'results': results
    }))


@login_required
@user_passes_test(lambda u: u.groups.filter(name="csv_uploaders").count() == 1, login_url="/admin/")
def csv_upload(request):
    import csv, zipfile, hashlib

    csv_file = request.FILES["csv_file"]
    dialect = csv.Sniffer().sniff(csv_file.read(1024), delimiters=";,")
    header_row = None
    photos_metadata = {}
    for row in csv.reader(csv_file, dialect):
        if not header_row:
            header_row = row
            continue
        row = dict(zip(header_row, row))
        photos_metadata[row.get("number")] = row

    zip_file = zipfile.ZipFile(request.FILES["zip_file"])
    album_id = request.POST.get('album_id')
    album = Album.objects.get(pk=album_id)
    licence = Licence.objects.get(name="Attribution-ShareAlike 4.0 International")

    for key in photos_metadata.keys():
        try:
            image_file = zip_file.read(key + ".jpeg")
        except KeyError:
            continue
        meta_for_this_image = photos_metadata[key]
        source_name = meta_for_this_image.get("institution") or "Ajapaik"
        try:
            source = Source.objects.get(description=source_name)
        except ObjectDoesNotExist:
            source = Source(name=source_name, description=source_name)
            source.save()
        try:
            Photo.objects.get(source=source, source_key=key)
            continue
        except ObjectDoesNotExist:
            pass
        extension = "jpeg"
        upload_file_name = "uploads/%s.%s" % (hashlib.md5(key).hexdigest(), extension)
        fout = open("/var/garage/" + upload_file_name, "w")
        fout.write(image_file)
        fout.close()
        place_name = meta_for_this_image.get("place") or "Ajapaik"
        try:
            area = Area.objects.get(name=place_name)
        except ObjectDoesNotExist:
            area = Area(name=place_name)
            area.save()
        description = '; '.join(filter(None, [meta_for_this_image[sub_key].strip() for sub_key in ('description', 'title') if sub_key in meta_for_this_image]))
        description = description.strip(' \t\n\r')
        source_url = meta_for_this_image.get("url")
        p = Photo(
            area=area,
            licence=licence,
            date_text=meta_for_this_image.get("date"),
            description=description,
            source=source,
            source_url=source_url,
            source_key=key,
            author=meta_for_this_image.get("author")
        )
        p.image.name = upload_file_name
        p.save()
        ap = AlbumPhoto(album=album, photo=p).save()
    return HttpResponse("OK")


def mapview_photo_upload_modal(request, photo_id):
    photo = get_object_or_404(Photo, pk=photo_id)
    licence = Licence.objects.get(name="Attribution-ShareAlike 4.0 International")
    return render_to_response('_photo_upload_modal.html', RequestContext(request, {
        'photo': photo,
        'licence': licence
    }))

def public_add_album(request):
    add_album_form = AddAlbumForm(request.POST)
    if add_album_form.is_valid():
        user_profile = request.get_user().profile
        name = add_album_form.cleaned_data["name"]
        description = add_album_form.cleaned_data["description"]
        if user_profile:
            new_album = Album(name=name, description=description, atype=Album.COLLECTION, profile=user_profile, is_public=False)
            new_album.save()
            selectable_albums = Album.objects.filter(Q(atype=Album.FRONTPAGE) | Q(profile=user_profile))
            selectable_albums = [{'id': x.id, 'name': x.name} for x in selectable_albums]
            return HttpResponse(json.dumps(selectable_albums), content_type="application/json")
    return HttpResponse(json.dumps("Error"), content_type="application/json", status=400)


def public_add_area(request):
    add_area_form = AddAreaForm(request.POST)
    if add_area_form.is_valid():
        try:
            existing_area = Area.objects.filter(name=add_area_form.cleaned_data["name"]).get()
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

def public_photo_upload(request):
    user_profile = request.get_user().profile
    area_selection_form = AreaSelectionForm(request.GET)
    add_album_form = AddAlbumForm()
    add_area_form = AddAreaForm()
    if area_selection_form.is_valid():
        area = Area.objects.get(pk=area_selection_form.cleaned_data['area'].id)
    else:
        area = Area.objects.get(pk=settings.DEFAULT_AREA_ID)
    selectable_albums = Album.objects.filter(Q(atype=Album.FRONTPAGE) | Q(profile=user_profile))
    selectable_areas = Area.objects.order_by('name').all()
    return render_to_response('photo_upload.html', RequestContext(request, {
        'area': area,
        'selectable_areas': selectable_areas,
        'selectable_albums': selectable_albums,
        'add_album_form': add_album_form,
        'add_area_form': add_area_form,
        'title': _("Timepatch (Ajapaik) - upload photos")
    }))

@ensure_csrf_cookie
def curator(request):
    curator_leaderboard = get_next_photos_to_geotag.get_leaderboard(request.get_user().profile.pk)
    last_created_album = Album.objects.filter(is_public=True).order_by('-created')[0]
    curator_random_image_ids = AlbumPhoto.objects.filter(album_id=last_created_album.id).order_by('?').values_list('id', flat=True)
    if not curator_random_image_ids or len(curator_random_image_ids) < 5:
        curator_random_image_ids = AlbumPhoto.objects.order_by('?').values_list('id', flat=True)
    curator_random_images = Photo.objects.filter(pk__in=curator_random_image_ids)[:5]
    site = Site.objects.get_current()
    return render_to_response('curator.html', RequestContext(request, {
        'description': _('Search for old photos, add them to Ajapaik, determine their locations ja share the resulting album!'),
        'curator_random_images': curator_random_images,
        'title': _("Timepatch (Ajapaik) - curate"),
        'hostname': 'http://%s' % (site.domain, ),
        'leaderboard': curator_leaderboard
    }))

def curator_search(request):
    if request.POST.get('testing'):
        return HttpResponse(open(os.path.join(os.path.dirname(__file__), 'curator_search_test_response.json'), 'r').read(), content_type="application/json")
    url = 'http://ajapaik.ee:8080/ajapaik-service/AjapaikService.json'
    full_search = request.POST.get('fullSearch') or None
    ids = request.POST.getlist('ids[]') or None
    response = None
    if ids is not None:
        ids_str = ['"' + each + '"' for each in ids]
        request_params = '{"method":"getRecords","params":[[%s]],"id":0}' % ','.join(ids_str)
        response = requests.post(url, data=request_params)
    if full_search is not None:
        full_search = full_search.encode('utf-8')
        request_params = '{"method":"search","params":[{"fullSearch":{"value":"%s"},"id":{"value":"","type":"OR"},"what":{"value":""},"description":{"value":""},"who":{"value":""},"from":{"value":""},"number":{"value":""},"luceneQuery":null,"institutionTypes":["MUSEUM",null,null],"pageSize":200,"digital":true}],"id":0}' % full_search
        response = requests.post(url, data=request_params)
    if response is not None:
        return HttpResponse(response, content_type="application/json")
    else:
        return HttpResponse([], content_type="application/json")

@csrf_exempt
def delete_public_photo(request, photo_id):
    user_profile = request.get_user().profile
    photo = None
    thirty_minutes_ago = datetime.datetime.now() - datetime.timedelta(minutes=30)
    try:
        photo = Photo.objects.filter(pk=photo_id, created__gte=thirty_minutes_ago).get()
    except ObjectDoesNotExist:
        pass
    if photo is not None:
        if photo.user_id == user_profile.user.id:
            photo.delete()
    return HttpResponse(json.dumps("Ok"), content_type="application/json")


def check_if_photo_in_ajapaik(request):
    source_desc = request.POST.get('source') or None
    source_key = request.POST.get('sourceKey') or None
    if source_desc is not None and source_key is not None:
        source_desc = source_desc.split(',')[0]
        try:
            source = Source.objects.get(description=source_desc)
            if source:
                try:
                    photo_count = Photo.objects.filter(source=source, source_key=source_key).count()
                    if photo_count > 0:
                        return HttpResponse(json.dumps(True), content_type="application/json")
                except ObjectDoesNotExist:
                    pass
        except ObjectDoesNotExist:
            pass
    return HttpResponse(json.dumps(False), content_type="application/json")


def curator_my_album_list(request):
    user_profile = request.get_user().profile
    serializer = CuratorMyAlbumListAlbumSerializer(
        Album.objects.filter(profile=user_profile, is_public=True).order_by('-created'), many=True
    )
    return HttpResponse(JSONRenderer().render(serializer.data), content_type="application/json")


def curator_selectable_albums(request):
    user_profile = request.get_user().profile
    serializer = CuratorAlbumSelectionAlbumSerializer(
        Album.objects.filter(
            # (Q(is_public=True) & Q(is_public_mutable=True)) |
            (Q(profile=user_profile) & Q(is_public=True)))
        .order_by('-created').all(), many=True
    )
    return HttpResponse(JSONRenderer().render(serializer.data), content_type="application/json")


# TODO: Replace with Django REST API
def curator_get_album_info(request):
    album_id = request.POST.get('albumId') or None
    if album_id is not None:
        try:
            album = Album.objects.get(pk=album_id)
            serializer = CuratorAlbumInfoSerializer(album)
        except ObjectDoesNotExist:
            return HttpResponse('Album does not exist', status=404)
        return HttpResponse(JSONRenderer().render(serializer.data), content_type='application/json')
    return HttpResponse('No album ID', status=500)


def curator_update_my_album(request):
    album_id = request.POST.get('albumId') or None
    user_profile = request.get_user().profile
    album_edit_form = CuratorAlbumEditForm(request.POST)
    if album_id is not None and user_profile and album_edit_form.is_valid():
        try:
            album = Album.objects.get(pk=album_id, profile=user_profile)
            album.name = album_edit_form.cleaned_data['name']
            album.description = album_edit_form.cleaned_data['description']
            album.save()
            return HttpResponse('OK', status=200)
        except ObjectDoesNotExist:
            return HttpResponse('Album does not exist', status=404)
    return HttpResponse('Faulty data', status=500)


def curator_photo_upload_handler(request):
    profile = request.get_user().profile

    area_name = request.POST.get("areaName")
    area_lat = request.POST.get("areaLat")
    area_lon = request.POST.get("areaLng")
    area = None
    try:
        area = Area.objects.filter(name=area_name).get()
    except ObjectDoesNotExist:
        if area_name and area_lat and area_lon:
            area = Area(
                name=area_name,
                lat=area_lat,
                lon=area_lon
            )
            area.save()

    curator_album_select_form = CuratorAlbumSelectionForm(request.POST)
    curator_album_create_form = AddAlbumForm(request.POST)

    selection_json = request.POST.get("selection") or None
    selection = None
    if selection_json is not None:
        selection = json.loads(selection_json)

    all_curating_points = []
    total_points_for_curating = 0
    ret = {
        "photos": {}
    }

    if selection and len(selection) > 0 and profile is not None and (curator_album_select_form.is_valid() or curator_album_create_form.is_valid()):
        album = None
        if curator_album_select_form.is_valid():
            if curator_album_select_form.cleaned_data['album'].profile == profile: #or curator_album_select_form.cleaned_data['album'].is_public_mutable == True:
                album = Album.objects.get(pk=curator_album_select_form.cleaned_data['album'].id)
        else:
            album = Album(
                name=curator_album_create_form.cleaned_data['name'],
                description=curator_album_create_form.cleaned_data['description'],
                atype=Album.CURATED,
                profile=profile,
                is_public=True,
                #is_public_mutable=curator_album_create_form.cleaned_data['is_public_mutable']
            )
            album.save()
        default_album = Album(
            name=str(profile.id) + "-" + str(datetime.datetime.now()).split('.')[0],
            atype=Album.AUTO,
            profile=profile,
            is_public=False,
            #is_public_mutable=False,
            subalbum_of=album
        )
        default_album.save()
        ret["album_id"] = album.id
        for (k, v) in selection.iteritems():
            upload_form = CuratorPhotoUploadForm(v)
            created_album_photo_links = []
            awarded_curator_points = []
            if upload_form.is_valid():
                if upload_form.cleaned_data['institution']:
                    upload_form.cleaned_data['institution'] = upload_form.cleaned_data['institution'].split(',')[0]
                    try:
                        source = Source.objects.get(description=upload_form.cleaned_data['institution'])
                    except ObjectDoesNotExist:
                        source = Source(name=upload_form.cleaned_data['institution'], description=upload_form.cleaned_data['institution'])
                        source.save()
                else:
                    source = Source.objects.get(name='AJP')
                existing_photo = None
                if upload_form.cleaned_data["identifyingNumber"] and upload_form.cleaned_data["identifyingNumber"] != "":
                    try:
                        existing_photo = Photo.objects.filter(source=source, source_key=upload_form.cleaned_data["identifyingNumber"]).get()
                    except ObjectDoesNotExist:
                        pass
                    if not existing_photo:
                        new_photo = None
                        if upload_form.cleaned_data["date"] == "[]":
                            upload_form.cleaned_data["date"] = None
                        try:
                            new_photo = Photo(
                                user=profile,
                                area=area,
                                author=upload_form.cleaned_data["creators"],
                                description=upload_form.cleaned_data["title"].rstrip(),
                                source=source,
                                types=upload_form.cleaned_data["types"],
                                date_text=upload_form.cleaned_data["date"],
                                licence=Licence.objects.get(name="Attribution-ShareAlike 4.0 International"),
                                source_key=upload_form.cleaned_data["identifyingNumber"],
                                source_url=upload_form.cleaned_data["urlToRecord"],
                                flip=upload_form.cleaned_data["flip"],
                                invert=upload_form.cleaned_data["invert"],
                                stereo=upload_form.cleaned_data["stereo"],
                            )
                            new_photo.save()
                            opener = urllib2.build_opener()
                            opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36")]
                            img_response = opener.open(upload_form.cleaned_data["imageUrl"])
                            new_photo.image.save("muis.jpg", ContentFile(img_response.read()))
                            if new_photo.invert:
                                photo_path = settings.MEDIA_ROOT + "/" + str(new_photo.image)
                                img = Image.open(photo_path)
                                inverted_grayscale_image = PIL.ImageOps.invert(img).convert('L')
                                inverted_grayscale_image.save(photo_path)
                            new_photo.width = new_photo.image.width
                            new_photo.height = new_photo.image.height
                            longest_side = max(new_photo.width, new_photo.height)
                            ret["photos"][k] = {}
                            if longest_side < 600:
                                ret["photos"][k]["message"] = _("This picture is small, we've allowed you to add it to specified album and you can mark it's location on the map, but it will be hidden from other users until we get a higher quality image from the institution.")
                            else:
                                ret["photos"][k]["message"] = _("OK")
                            new_photo.save()
                            points_for_curating = Points(action=Points.PHOTO_CURATION, photo=new_photo, points=50, user=profile, created=new_photo.created)
                            points_for_curating.save()
                            awarded_curator_points.append(points_for_curating)
                            if album:
                                ap = AlbumPhoto(photo=new_photo, album=album)
                                ap.save()
                                created_album_photo_links.append(ap)
                            ap = AlbumPhoto(photo=new_photo, album=default_album)
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
                        if album:
                            ap = AlbumPhoto(photo=existing_photo, album=album)
                            ap.save()
                        ap = AlbumPhoto(photo=existing_photo, album=default_album)
                        ap.save()
                        ret["photos"][k] = {}
                        ret["photos"][k]["success"] = True
                        ret["photos"][k]["message"] = _("Photo already exists in Ajapaik")
        requests.post('https://graph.facebook.com/?id=' + (request.build_absolute_uri(reverse('project.home.views.game')) + '?album=' + str(album.id)) + '&scrape=true')
        for cp in all_curating_points:
            total_points_for_curating += cp.points
        ret["total_points_for_curating"] = total_points_for_curating
    else:
        if not selection or len(selection) == 0:
            error = _("Please add photos to your album")
        else:
            error = _("Not enough data submitted")
        ret = {
            "error": error
        }
    return HttpResponse(json.dumps(ret), content_type="application/json")

def public_photo_upload_handler(request):
    profile = request.get_user().profile
    if "fb_access_token" in request.POST:
        token = request.POST.get("fb_access_token")
        profile, fb_data = Profile.facebook.get_user(token)
        if profile is None:
            user = request.get_user()
            profile = user.profile
            profile.update_from_fb_data(token, fb_data)
    uploaded_file = request.FILES.get("files[]", None)
    area_id = int(request.POST.get("areaId"))
    album_ids = request.POST.get("albumIds")
    album_ids_int = None
    try:
        album_ids_int = [int(x) for x in album_ids.split(',')]
    except ValueError:
        pass
    photo_upload_form = PublicPhotoUploadForm(request.POST)
    albums = None
    area = None
    error = None
    uploaded_file_name = None
    new_photo = None
    created_album_photo_links = []
    try:
        albums = Album.objects.filter(pk__in=album_ids_int).all()
    except ObjectDoesNotExist:
        pass
    except ValueError:
        pass
    try:
        area = Area.objects.filter(pk=area_id).get()
    except ObjectDoesNotExist:
        pass
    ret = {"files": []}
    if photo_upload_form.is_valid():
        if photo_upload_form.cleaned_data['institution']:
            try:
                source = Source.objects.get(description=photo_upload_form.cleaned_data['institution'])
            except ObjectDoesNotExist:
                source = Source(name=photo_upload_form.cleaned_data['institution'], description=photo_upload_form.cleaned_data['institution'])
                source.save()
        else:
            source = Source.objects.get(name='AJP')
        existing_photo = None
        if photo_upload_form.cleaned_data["number"] and photo_upload_form.cleaned_data["number"] != "":
            try:
                existing_photo = Photo.objects.filter(source=source, source_key=photo_upload_form.cleaned_data["number"]).get()
            except:
                pass
        if profile is not None and uploaded_file is not None and area is not None and existing_photo is None:
            try:
                uploaded_file_name = uploaded_file.name
                fileobj = handle_uploaded_file(uploaded_file)
                if photo_upload_form.cleaned_data["title"] == "":
                    photo_upload_form.cleaned_data["title"] = None
                if photo_upload_form.cleaned_data["description"] == "":
                    photo_upload_form.cleaned_data["description"] = None
                if photo_upload_form.cleaned_data["licence"] == "":
                    photo_upload_form.cleaned_data["licence"] = None
                if photo_upload_form.cleaned_data["date"] == "":
                    photo_upload_form.cleaned_data["date"] = None
                if photo_upload_form.cleaned_data["number"] == "":
                    photo_upload_form.cleaned_data["number"] = None
                if photo_upload_form.cleaned_data["url"] == "":
                    photo_upload_form.cleaned_data["url"] = None
                new_photo = Photo(
                    user=profile,
                    area_id=area_id,
                    title=photo_upload_form.cleaned_data["title"],
                    description=photo_upload_form.cleaned_data["description"],
                    source=source,
                    date_text=photo_upload_form.cleaned_data["date"],
                    licence=photo_upload_form.cleaned_data["licence"],
                    source_key=photo_upload_form.cleaned_data["number"],
                    source_url=photo_upload_form.cleaned_data["url"]
                )
                new_photo.save()
                new_photo.image.save(uploaded_file.name, fileobj)
                points_for_uploading = Points(action=Points.PHOTO_UPLOAD, photo=new_photo, points=50, user=profile, created=new_photo.created)
                points_for_uploading.save()
                if albums:
                    for a in albums:
                        ap = AlbumPhoto(photo=new_photo, album=a)
                        ap.save()
                        created_album_photo_links.append(ap)
            except:
                if new_photo:
                    new_photo.delete()
                for ap in created_album_photo_links:
                    ap.delete()
                error = _("Error uploading file")
            if new_photo is not None:
                try:
                    _extract_and_save_data_from_exif(new_photo)
                except:
                    pass
        else:
            error = _("Conflicting data submitted (no photos, no user or faulty areas)")
        if error is None:
            ret["files"].append({
                "name": uploaded_file_name,
                "url": reverse('project.home.views.photo', args=(new_photo.id,)),
                "thumbnailUrl": reverse('project.home.views.photo_thumb', args=(new_photo.id,)),
                "deleteUrl": reverse('project.home.views.delete_public_photo', args=(new_photo.id,)),
                "points": 50,
                "deleteType": "POST"
            })
        else:
            ret["files"].append({
                "name": uploaded_file_name,
                "error": error
            })
    else:
        ret["files"].append({
            "name": uploaded_file_name,
            "error": _("Invalid form data")
        })
    return HttpResponse(json.dumps(ret), content_type="application/json")


def pane_contents(request):
    marker_ids = request.POST.getlist('marker_ids[]')
    data = []
    for p in Photo.objects.filter(lat__isnull=False, lon__isnull=False, rephoto_of__isnull=True, id__in=marker_ids):
        rephoto_count = len(list(Photo.objects.filter(rephoto_of=p.id)))
        im_url = reverse('project.home.views.photo_thumb', args=(p.id,))
        try:
            if p.image._get_width() >= p.image._get_height():
                thumb_str = "%d"
            else:
                thumb_str = "x%d"
            im = get_thumbnail(p.image, thumb_str % 150, crop="center")
            data.append([p.id, im_url, rephoto_count, p.flip, p.description, p.azimuth, im._size[0], im._size[1]])
        except IOError:
            pass

    return render_to_response('pane_contents.html', RequestContext(request, {"data": data}))

@ensure_csrf_cookie
def grid(request):
    area_selection_form = AreaSelectionForm(request.GET)

    if area_selection_form.is_valid():
        area = Area.objects.get(pk=area_selection_form.cleaned_data['area'].id)
        qs = Photo.objects.filter(area_id=area.id)

        data = qs.get_old_photos_for_grid_view(0, settings.GRID_VIEW_PAGE_SIZE)
        photo_count = qs.get_old_photo_count_for_grid_view()

        photo_ids_user_has_looked_at = UserMapView.objects.filter(user_profile=request.get_user().profile).values_list(
            'photo_id', flat=True)
        keys = {}
        for e in photo_ids_user_has_looked_at:
            keys[e] = 1
        photo_ids_user_has_looked_at = keys

        return render_to_response('grid.html', RequestContext(request, {
            "data": data,
            "photo_count": photo_count,
            "area": area,
            "start": 0,
            "area_selection_form": area_selection_form,
            "page_size": settings.GRID_VIEW_PAGE_SIZE,
            #"user_seen_photo_ids": photo_ids_user_has_looked_at,
        }))


def grid_infinite_scroll(request):
    area_selection_form = AreaSelectionForm(request.GET)

    data = []
    if area_selection_form.is_valid():
        area = Album.objects.get(pk=area_selection_form.cleaned_data['area'].id)
        qs = Photo.objects.filter(area_id=area.id)
        start = int(request.GET.get('start'))
        data = qs.get_old_photos_for_grid_view(start, start + settings.GRID_VIEW_PAGE_SIZE)
    return HttpResponse(json.dumps(data), content_type="application/json")

def locloud_locator(request):
    print request.POST