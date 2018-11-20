import json

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse

from project.ajapaik.forms import FaceRectangleSubmitForm
from project.ajapaik.models import FaceRecognitionRectangle
from project.ajapaik.then_and_now_tours import user_has_confirmed_email


@user_passes_test(user_has_confirmed_email, login_url='/accounts/login/')
def add_subject(request):
    pass


def add_rectangle(request):
    profile = request.get_user().profile
    form = FaceRectangleSubmitForm(request.POST.copy())
    if form.is_valid():
        photo = form.cleaned_data['photo']
        width_scale = form.cleaned_data['seen_width'] / photo.width
        height_scale = form.cleaned_data['seen_height'] / photo.height
        # jQuery plugin gives x1, y1 topLeft, x2, y2 bottomRight
        # DB stores (top, right, bottom, left)
        coordinates = [
            int(form.cleaned_data['y1'] * height_scale),
            int(form.cleaned_data['x2'] * width_scale),
            int(form.cleaned_data['y2'] * height_scale),
            int(form.cleaned_data['x1'] * width_scale)
        ]
        new_rectangle = FaceRecognitionRectangle(
            photo=form.cleaned_data['photo'],
            coordinates=json.dumps(coordinates),
            user_id=profile.id
        ).save()
        # p.latest_dating = dating.created
        # if not p.first_dating:
        #     p.first_dating = dating.created
        # p.light_save()
        # TODO: Points system
        # Points(
        #     user=profile,
        #     action=Points.DATING,
        #     photo=form.cleaned_data['photo'],
        #     dating=dating,
        #     points=DATING_POINTS,
        #     created=dating.created
        # ).save()

        return HttpResponse('OK')
    else:
        return HttpResponse('Invalid data', status=400)
