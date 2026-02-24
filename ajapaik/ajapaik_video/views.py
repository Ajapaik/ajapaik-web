import json

import unicodedata
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.translation import gettext as _

from ajapaik.ajapaik.forms import VideoStillCaptureForm
from ajapaik.ajapaik.models import Video, Photo, Source, AlbumPhoto, Points
from ajapaik.ajapaik.utils import is_ajax


def videoslug(request, video_id, pseudo_slug=None):
    video = get_object_or_404(Video, pk=video_id)
    if is_ajax(request):
        template = 'video/_video_modal.html'
    else:
        template = 'video/videoview.html'

    return render(request, template, {'video': video, })


def generate_still_from_video(request):
    profile = request.get_user().profile
    form = VideoStillCaptureForm(request.POST)
    context = {}
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
                    reverse('photo', args=(still.id, still.get_pseudo_slug)))
                still.image.save(
                    f'{unicodedata.normalize("NFKD", description)}.jpeg',
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
                still.add_to_source_album()
        context['stillId'] = still.id

    return HttpResponse(json.dumps(context), content_type='application/json')
