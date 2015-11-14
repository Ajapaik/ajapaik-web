from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django import forms

from project.ajapaik.models import TourRephoto


class camera_upload_form(forms.Form):
    fileToUpload = forms.ImageField()


def frontpage(request):
    ret = {
        'is_frontpage': True
    }
    return render_to_response('then_and_now/frontpage.html', RequestContext(request, ret))


def map_view(request, tour_id=None):
    ret = {

    }
    return render_to_response('then_and_now/map.html', RequestContext(request, ret))


def gallery(request, tour_id):
    ret = {

    }
    return render_to_response('then_and_now/gallery.html', RequestContext(request, ret))


def detail(request, photo_id):
    ret = {

    }

    return render_to_response('then_and_now/detail.html', RequestContext(request, ret))


def pair(request, original_photo_id, rephoto_id):
    ret = {

    }

    return render_to_response('then_and_now/pair.html', RequestContext(request, ret))


def camera(request, photo_id):
    ret = {

    }

    return render_to_response('then_and_now/camera.html', RequestContext(request, ret))


@csrf_exempt
def camera_upload(request):
    ret = {

    }
    form = camera_upload_form(request.POST, request.FILES)
    if form.is_valid():
        TourRephoto(
            image=form.cleaned_data['image']
        ).save()
    else:
        ret['errors'] = form.errors
        print form.errors

    return HttpResponse(ret)


def tour_complete(request, photo_id):
    ret = {

    }

    return render_to_response('then_and_now/tour_complete.html', RequestContext(request, ret))


def juhan(request):
    ret = {

    }
    return render_to_response('then_and_now/google.html', RequestContext(request, ret))
