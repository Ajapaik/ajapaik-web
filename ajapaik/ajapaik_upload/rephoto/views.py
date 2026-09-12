import json
import time
from copy import deepcopy
from datetime import timedelta
from io import BytesIO
from time import strftime, strptime

from PIL import Image
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.db.transaction import atomic
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt

from ajapaik.ajapaik.models import Photo, Licence, GeoTag, _calc_trustworthiness
from ajapaik.ajapaik.photo_utils import _extract_and_save_data_from_exif


@atomic
@csrf_exempt
def rephoto_upload(request, photo_id):
    if request.method != 'POST':
        return HttpResponse(json.dumps({'message': 'Unsupported HTTP Method'}), status=405,
                            content_type='application/json')

    photo = get_object_or_404(Photo, pk=photo_id)
    profile = request.get_user().profile
    django_user = request.get_user()
    social_account = SocialAccount.objects.filter(user=request.user).first()
    if not social_account and not django_user.email and not (django_user.is_superuser or django_user.is_staff):
        return HttpResponse(json.dumps({'error': _('Non-authenticated user')}), content_type='application/json')

    client_upload_id = request.POST.get('client_upload_id')
    lock_key = f'rephoto_lock_{client_upload_id}' if client_upload_id else None

    if client_upload_id:
        cached_id = cache.get(f'rephoto_upload_{client_upload_id}')
        if cached_id:
            return HttpResponse(json.dumps({'new_id': cached_id}), content_type='application/json')

        if cache.get(lock_key):
            for _ in range(30):
                time.sleep(0.5)
                cached_id = cache.get(f'rephoto_upload_{client_upload_id}')
                if cached_id:
                    return HttpResponse(json.dumps({'new_id': cached_id}), content_type='application/json')
                if not cache.get(lock_key):
                    break
        cache.set(lock_key, True, 60)

    try:
        def parse_float(val):
            if val not in (None, '', 'null', 'undefined'):
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return None
            return None

        data = request.POST
        scale_factor = parse_float(data.get('scale_factor'))
        cam_scale_factor = round(scale_factor, 6) if scale_factor is not None else None
        rephoto_lat = parse_float(data.get('lat'))
        rephoto_lon = parse_float(data.get('lon'))
        rephoto_yaw = parse_float(data.get('yaw'))

        # Check for recent duplicate (within 2 minutes by same user for same parent photo)
        recent_dup_qs = Photo.objects.filter(
            rephoto_of=photo,
            user=profile,
            created__gte=timezone.now() - timedelta(minutes=2),
            cam_scale_factor=cam_scale_factor,
            lat=rephoto_lat,
            lon=rephoto_lon,
        )
        if rephoto_yaw is not None:
            recent_dup_qs = recent_dup_qs.filter(cam_yaw=rephoto_yaw)

        recent_duplicate = recent_dup_qs.order_by('-created').first()
        if recent_duplicate:
            if client_upload_id:
                cache.set(f'rephoto_upload_{client_upload_id}', recent_duplicate.pk, 3600)
            return HttpResponse(json.dumps({'new_id': recent_duplicate.pk}), content_type='application/json')

        new_id = None
        for f in request.FILES.getlist("user_file[]"):
            date_taken = data.get('dateTaken', None)
            parsed_date_taken = None

            if date_taken:
                try:
                    parsed_date_taken = strftime('%Y-%m-%d %H:%M', strptime(date_taken, '%d.%m.%Y %H:%M'))
                except:  # noqa
                    pass

            file_obj = ContentFile(f.read())

            rephoto = Photo(
                rephoto_of=photo,
                area=photo.area,
                licence=Licence.objects.get(id=17),  # CC BY 4.0
                description=data.get('description', photo.get_display_text),
                lat=rephoto_lat,
                lon=rephoto_lon,
                date_text=data.get('date_text', None),
                user=profile,
                cam_scale_factor=cam_scale_factor,
                cam_yaw=rephoto_yaw,
                cam_pitch=parse_float(data.get('pitch')),
                cam_roll=parse_float(data.get('roll')),
            )
            if parsed_date_taken:
                photo.date = parsed_date_taken

            rephoto.save()
            rephoto.image.save('rephoto.jpg', file_obj)
            rephoto.set_aspect_ratio()
            rephoto.find_similar()

            # Image saved to disk, can analyse now
            new_id = rephoto.pk
            img = Image.open(f'{settings.MEDIA_ROOT}/{str(rephoto.image)}')
            _extract_and_save_data_from_exif(rephoto)

            if rephoto.lat is not None and rephoto.lon is not None:
                # Use azimuth if available (ensure 0 is not treated as falsy in downstream calculations)
                azimuth_val = rephoto.cam_yaw
                if azimuth_val == 0:
                    azimuth_val = 360.0

                trust = max(_calc_trustworthiness(profile.id) if profile else 0.1, 0.1)

                rephoto_geotag = GeoTag(
                    lat=rephoto.lat,
                    lon=rephoto.lon,
                    azimuth=azimuth_val,
                    origin=GeoTag.REPHOTO,
                    type=GeoTag.GPS,
                    map_type=GeoTag.NO_MAP,
                    photo=photo,
                    trustworthiness=trust,
                    is_correct=False,
                    user=profile,
                )
                rephoto_geotag.save()
                if not photo.first_geotag:
                    photo.first_geotag = rephoto.created
                photo.latest_geotag = rephoto.created
                photo.set_calculated_fields()
                if photo.azimuth is None and azimuth_val is not None:
                    photo.azimuth = azimuth_val
                    rephoto_geotag.azimuth_correct = True
                    rephoto_geotag.save(update_fields=['azimuth_correct'])

                for a in photo.albums.all():
                    qs = a.get_geotagged_historic_photo_queryset_with_subalbums()
                    a.geotagged_photo_count_with_subalbums = qs.count()
                    a.save(update_fields=['geotagged_photo_count_with_subalbums'])

            if not photo.first_rephoto:
                photo.first_rephoto = rephoto.created
            photo.latest_rephoto = rephoto.created
            photo.save()

            for each in photo.albums.all():
                each.rephoto_count_with_subalbums = each.get_rephotos_queryset_with_subalbums().count()
                each.save(update_fields=['rephoto_count_with_subalbums'])

            rephoto.image.save('rephoto.jpg', file_obj)

            cropped_file = request.FILES.get('cropped_file')

            if cropped_file:
                rephoto.image_unscaled = deepcopy(rephoto.image)
                rephoto.image.save('rephoto.jpg', ContentFile(cropped_file.read()))
            elif rephoto.cam_scale_factor:
                new_size = tuple([int(x * rephoto.cam_scale_factor) for x in img.size])
                output_file = BytesIO()

                if rephoto.cam_scale_factor < 1:
                    x0 = (img.size[0] - new_size[0]) // 2
                    y0 = (img.size[1] - new_size[1]) // 2
                    x1 = img.size[0] - x0
                    y1 = img.size[1] - y0
                    new_img = img.transform(new_size, Image.EXTENT, (x0, y0, x1, y1))
                    new_img.save(output_file, 'JPEG', quality=95)
                elif rephoto.cam_scale_factor > 1:
                    x0 = (new_size[0] - img.size[0]) // 2
                    y0 = (new_size[1] - img.size[1]) // 2
                    new_img = Image.new('RGB', new_size)
                    new_img.paste(img, (x0, y0))
                    new_img.save(output_file, 'JPEG', quality=95)

                rephoto.image_unscaled = deepcopy(rephoto.image)
                rephoto.image.save(str(rephoto.image), ContentFile(output_file.getvalue()))

        profile.update_rephoto_score()
        profile.set_calculated_fields()

        if client_upload_id and new_id:
            cache.set(f'rephoto_upload_{client_upload_id}', new_id, 3600)

        return HttpResponse(json.dumps({'new_id': new_id}), content_type='application/json')
    finally:
        if lock_key:
            cache.delete(lock_key)


from django.contrib.auth.decorators import login_required


@login_required
def rephoto_capture(request, photo_id):
    from django.shortcuts import render
    photo = get_object_or_404(Photo, pk=photo_id)
    return render(request, 'rephoto_upload/capture.html', {'photo': photo})
