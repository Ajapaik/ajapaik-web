import json
from copy import deepcopy
from io import StringIO
from time import strftime, strptime

from PIL import Image
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.core.files.base import ContentFile
from django.db.transaction import atomic
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt

from ajapaik.ajapaik.models import Photo, Licence
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
    if not social_account and not django_user.email:
        return HttpResponse(json.dumps({'error': _('Non-authenticated user')}), content_type='application/json')

    for f in request.FILES.getlist("user_file[]"):
        data = request.POST
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
            lat=data.get('lat', None),
            lon=data.get('lon', None),
            date_text=data.get('date_text', None),
            user=profile,
            cam_scale_factor=round(float(data['scale_factor']), 6) if data.get('scale_factor') else None,
            cam_yaw=data.get('yaw'),
            cam_pitch=data.get('pitch'),
            cam_roll=data.get('roll'),
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

        if not photo.first_rephoto:
            photo.first_rephoto = rephoto.created
        photo.latest_rephoto = rephoto.created
        photo.rephoto_count = photo.rephoto_count + 1
        photo.save(update_fields=['first_rephoto', 'latest_rephoto', 'rephoto_count'])

        for each in photo.albums.all():
            each.rephoto_count_with_subalbums = each.get_rephotos_queryset_with_subalbums().count()
            each.save(update_fields=['rephoto_count_with_subalbums'])

        rephoto.image.save('rephoto.jpg', file_obj)

        if rephoto.cam_scale_factor:
            new_size = tuple([int(x * rephoto.cam_scale_factor) for x in img.size])
            output_file = StringIO()

            if rephoto.cam_scale_factor < 1:
                x0 = (img.size[0] - new_size[0]) / 2
                y0 = (img.size[1] - new_size[1]) / 2
                x1 = img.size[0] - x0
                y1 = img.size[1] - y0
                new_img = img.transform(new_size, Image.EXTENT, (x0, y0, x1, y1))
                new_img.save(output_file, 'JPEG', quality=95)
            elif rephoto.cam_scale_factor > 1:
                x0 = (new_size[0] - img.size[0]) / 2
                y0 = (new_size[1] - img.size[1]) / 2
                new_img = Image.new('RGB', new_size)
                new_img.paste(img, (x0, y0))
                new_img.save(output_file, 'JPEG', quality=95)

            rephoto.image_unscaled = deepcopy(rephoto.image)
            rephoto.image.save(str(rephoto.image), ContentFile(output_file.getvalue()))

    profile.update_rephoto_score()
    profile.set_calculated_fields()

    return HttpResponse(json.dumps({'new_id': new_id}), content_type='application/json')
