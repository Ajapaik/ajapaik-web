# encoding: utf-8
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.db.models import Sum, Q

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
from django.contrib.gis.geos import Polygon
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt

from project.home.models import Photo, Profile, Source, Device, DifficultyFeedback, GeoTag, FlipFeedback, UserMapView, Points, \
    Album, AlbumPhoto, Area
from project.home.forms import AddAlbumForm, PublicPhotoUploadForm, AreaSelectionForm, AlbumSelectionForm, AddAreaForm
from sorl.thumbnail import get_thumbnail
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True
from PIL.ExifTags import TAGS, GPSTAGS
from time import strftime, strptime
from StringIO import StringIO
from copy import deepcopy

import get_next_photos_to_geotag
import random
import datetime
import json

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
                exif_data[decoded + '.' + sub_decoded] = value[t]

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
                device = Device(camera_make=camera_make, camera_model=camera_model, lens_make=lens_make, lens_model=lens_model, software=software)
                device.save()
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
                    parsed_date_taken = strptime(date_taken, "%d.%m.%Y %H:%M")
                    re_photo.date = strftime("%Y-%m-%d %H:%M", parsed_date_taken)
                if re_photo.cam_scale_factor:
                    re_photo.cam_scale_factor = round(float(re_photo.cam_scale_factor), 6)
                re_photo.save()
                re_photo.image.save(f.name, fileobj)
                new_id = re_photo.pk

                img = Image.open(settings.MEDIA_ROOT + "/" + str(re_photo.image))
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
                        new_img = Image.new("RGB", new_size)
                        new_img.paste(img, (x0, y0))
                        new_img.save(output_file, 'JPEG', quality=95)
                        re_photo.image_unscaled = deepcopy(re_photo.image)
                        re_photo.image.save(str(re_photo.image), ContentFile(output_file.getvalue()))

        profile.update_rephoto_score()

    return HttpResponse(json.dumps({'new_id': new_id}), content_type="application/json")


def logout(request):
    from django.contrib.auth import logout

    logout(request)
    return redirect(request.META['HTTP_REFERER'])


def calculate_recent_activity_scores():
    thousand_actions_ago = Points.objects.order_by('-created')[1000].created
    recent_actions = Points.objects.filter(created__gt=thousand_actions_ago).values('user_id').annotate(total_points=Sum('points'))
    for each in recent_actions:
        profile = Profile.objects.filter(user_id=each['user_id'])[:1].get()
        profile.score_recent_activity = each['total_points']
        profile.save()

@ensure_csrf_cookie
def game(request):
    ctx = {}
    area_selection_form = AreaSelectionForm(request.GET)

    if area_selection_form.is_valid():
        ctx['area'] = Area.objects.get(pk=area_selection_form.cleaned_data['area'].id)
    else:
        ctx['area'] = Area.objects.get(pk=settings.DEFAULT_AREA_ID)

    site = Site.objects.get_current()
    ctx['hostname'] = 'http://%s' % (site.domain, )
    ctx['title'] = _('Guess the location')
    ctx['is_game'] = True

    ctx['area_selection_form'] = area_selection_form

    return render_to_response('game.html', RequestContext(request, ctx))


def frontpage(request):
    try:
        example = random.choice(Photo.objects.filter(
            id__in=[2483, 2495, 2502, 3193, 3195, 3201, 3203, 3307, 4821, 5485, 5535, 5588, 5617, 5644, 5645, 5646],
            rephoto_of__isnull=False))
    except ObjectDoesNotExist:
        example = random.choice(Photo.objects.filter(rephoto_of__isnull=False)[:8])
    example_source = Photo.objects.get(pk=example.rephoto_of.id)
    area_selection_form = AreaSelectionForm(request.GET)

    if not area_selection_form.is_valid():
        area_selection_form = AreaSelectionForm()

    return render_to_response('frontpage.html', RequestContext(request, {
        'area_selection_form': area_selection_form,
        'example': example,
        'example_source': example_source,
        'grid_view_enabled': settings.GRID_VIEW_ENABLED,
        'photo_upload_enabled': settings.PUBLIC_PHOTO_UPLOAD_ENABLED
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
    image_to_use = p.image_unscaled or p.image
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

    site = Site.objects.get_current()
    template = ['', '_photo_modal.html', 'photoview.html'][request.is_ajax() and 1 or 2]
    if not photo_obj.description:
        title = "Unknown photo"
    else:
        title = ' '.join(photo_obj.description.split(' ')[:5])[:50]

    area_selection_form = AreaSelectionForm({'area': photo_obj.area.id})

    return render_to_response(template, RequestContext(request, {
        'photo': photo_obj,
        'area': photo_obj.area,
        'area_selection_form': area_selection_form,
        'fullscreen': _make_fullscreen(photo_obj),
        'rephoto_fullscreen': _make_fullscreen(rephoto),
        'title': title,
        'description': photo_obj.description,
        'rephoto': rephoto,
        'hostname': 'http://%s' % (site.domain, ),
        'is_photoview': True
    }))


@ensure_csrf_cookie
def mapview(request, photo_id=None, rephoto_id=None):
    area_selection_form = AreaSelectionForm(request.GET)

    if area_selection_form.is_valid():
        area = Area.objects.get(pk=area_selection_form.cleaned_data['area'].id)
    else:
        area = Area.objects.get(pk=settings.DEFAULT_AREA_ID)

    if area:
        title = area.name + ' - ' + _('Browse photos on map')
    else:
        title = _('Browse photos on map')

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

    if selected_photo and not area:
        area = Area.objects.get(pk=selected_photo.areas[0].id)

    photo_ids_user_has_looked_at = UserMapView.objects.filter(user_profile=request.get_user().profile).values_list(
        'photo_id', flat=True)
    keys = {}
    for e in photo_ids_user_has_looked_at:
        keys[e] = 1
    photo_ids_user_has_looked_at = keys

    return render_to_response('mapview.html', RequestContext(request, {
        'area': area,
        'title': title,
        'area_selection_form': area_selection_form,
        #'user_seen_photo_ids': photo_ids_user_has_looked_at,
        'selected_photo': selected_photo,
        'selected_rephoto': selected_rephoto,
        'is_mapview': True
    }))


def map_objects_by_bounding_box(request):
    data = request.POST

    qs = Photo.objects.all()

    bounding_box = Polygon.from_bbox((data.get('sw_lat'), data.get('sw_lon'), data.get('ne_lat'), data.get('ne_lon')))

    ungeotagged_count, geotagged_count = qs.get_area_photo_count_and_total_geotag_count(data.get('area_id'))

    if data.get('zoom') > 15:
        data = qs.get_geotagged_photos_list(bounding_box, True)
    else:
        data = qs.get_geotagged_photos_list(bounding_box, False)

    data = {'photos': data, 'geotagged_count': geotagged_count, 'ungeotagged_count': ungeotagged_count}

    return HttpResponse(json.dumps(data), content_type="application/json")


def get_leaderboard(request):
    return HttpResponse(json.dumps(get_next_photos_to_geotag.get_leaderboard(request.get_user().profile.pk)), content_type="application/json")


def geotag_add(request):
    data = request.POST
    origin = data.get('origin')
    if origin == 'Grid':
        origin = GeoTag.GRID
    elif origin == 'Map':
        origin = GeoTag.MAP
    else:
        origin = GeoTag.GAME
    location_correct, location_uncertain, this_guess_score, feedback_message, all_geotags_latlng_for_this_photo, azimuth_tags_count, new_estimated_location, confidence = get_next_photos_to_geotag.submit_guess(
        request.get_user().profile, data.get('photo_id'), data.get('lon'), data.get('lat'),
        hint_used=data.get('hint_used'), azimuth=data.get('azimuth'), zoom_level=data.get('zoom_level'),
        azimuth_line_end_point=data.getlist('azimuth_line_end_point[]'), origin=origin)
    flip = data.get("flip", None)
    if flip is not None:
        flip_feedback = FlipFeedback()
        flip_feedback.photo_id = data['photo_id']
        flip_feedback.user_profile = request.get_user().profile
        if flip == "true":
            flip_feedback.flip = True
        elif flip == "false":
            flip_feedback.flip = False
        flip_feedback.save()
    return HttpResponse(json.dumps({
        'is_correct': location_correct,
        'location_is_unclear': location_uncertain,
        'current_score': this_guess_score,
        'confidence': confidence,
        'heatmap_points': all_geotags_latlng_for_this_photo,
        'feedback_message': feedback_message,
        'azimuth_tags': azimuth_tags_count,
        'estimated_location': new_estimated_location
    }), content_type="application/json")


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

    if area_selection_form.is_valid():
        area = Area.objects.get(pk=area_selection_form.cleaned_data['area'].id)
    else:
        area = Area.objects.get(pk=settings.DEFAULT_AREA_ID)

    album_selection_form = AlbumSelectionForm(request.GET)

    if album_selection_form.is_valid():
        album = Album.objects.get(pk=album_selection_form.cleaned_data['album'].id)
    else:
        album = None

    qs = Photo.objects.filter(area_id=area.id)

    if album is not None:
        photos_ids_in_album = AlbumPhoto.objects.filter(album=album).values_list('photo_id', flat=True)
        qs = qs.filter(pk__in=photos_ids_in_album)

    # TODO: [0][0] Wtf?
    data = {"photo": qs.get_next_photo_to_geotag(request)[0][0], "user_seen_all": qs.get_next_photo_to_geotag(request)[1],
            "nothing_more_to_show": qs.get_next_photo_to_geotag(request)[2]}

    return HttpResponse(json.dumps(data), content_type="application/json")


def difficulty_feedback(request):
    # TODO: Tighten down security when it becomes apparent people are abusing this

    user_profile = request.get_user().profile
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
@user_passes_test(lambda u: u.groups.filter(name="csv_uploaders").count() == 0, login_url="/admin/")
def csv_upload(request):
    pass
    # import csv, zipfile, hashlib
    #
    # csv_file = request.FILES["csv_file"]
    # dialect = csv.Sniffer().sniff(csv_file.read(1024), delimiters=";,")
    # header_row = None
    # photos_metadata = {}
    # for row in csv.reader(csv_file, dialect):
    #     if not header_row:
    #         header_row = row
    #         continue
    #     row = dict(zip(header_row, row))
    #     photos_metadata[row.get("image")] = row
    #
    # zip_file = zipfile.ZipFile(request.FILES["zip_file"])
    #
    # for key in photos_metadata.keys():
    #     try:
    #         image_file = zip_file.read(key)
    #     except KeyError:
    #         continue
    #     meta_for_this_image = photos_metadata[key]
    #     source_key = meta_for_this_image.get("number") or key
    #     try:
    #         existing_photo = Photo.objects.get(source_key=source_key)
    #         continue
    #     except ObjectDoesNotExist:
    #         pass
    #     extension = key.split(".")[-1]
    #     upload_file_name = "uploads/%s.%s" % (hashlib.md5(key).hexdigest(), extension)
    #     fout = open("/var/garage/" + upload_file_name, "w")
    #     fout.write(image_file)
    #     fout.close()
    #     place_name = meta_for_this_image.get("place") or "Ajapaik"
    #     try:
    #         album = Album.objects.get(name=place_name)
    #     except ObjectDoesNotExist:
    #         album = Album(name=place_name, atype=Album.COLLECTION, is_public=True)
    #         album.save()
    #     description = '; '.join(filter(None,
    #                                    [meta_for_this_image[sub_key].strip() for sub_key in ('description', 'title') if
    #                                     sub_key in meta_for_this_image]))
    #     source_name = meta_for_this_image.get("institution") or "Ajapaik"
    #     try:
    #         source = Source.objects.get(description=source_name)
    #     except ObjectDoesNotExist:
    #         source = Source(name=source_name, description=source_name)
    #         source.save()
    #     source_url = meta_for_this_image.get("url")
    #     p = Photo(date_text=meta_for_this_image.get("date"),description=description, source=source,
    #               source_url=source_url, source_key=source_key)
    #     p.image.name = upload_file_name
    #     p.save()
    #     ap = AlbumPhoto(album=album, photo=p)
    #     ap.save()
    # return HttpResponse("OK")


def mapview_photo_upload_modal(request, photo_id):
    photo = get_object_or_404(Photo, pk=photo_id)
    return render_to_response('_photo_upload_modal.html', RequestContext(request, {
        'photo': photo
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
            return HttpResponse(json.dumps("Ok"), content_type="application/json")
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
                return HttpResponse(json.dumps("Ok"), content_type="application/json")
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

def curator(request):
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
    return render_to_response('curator.html', RequestContext(request, {
        'area': area,
        'selectable_areas': selectable_areas,
        'selectable_albums': selectable_albums,
        'add_album_form': add_album_form,
        'add_area_form': add_area_form,
        'title': _("Timepatch (Ajapaik) - curate")
    }))

def curator_search(request):
    return HttpResponse(json.dumps("Ok"), content_type="application/json")

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
                points_for_uploading = Points(action=Points.PHOTO_UPLOAD, action_reference=new_photo.id, points=50, user=profile, created=new_photo.created)
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