# encoding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
from django.utils import simplejson as json

from project.models import Photo
from project.forms import GeoTagAddForm

import get_next_photos_to_geotag

def test1(request):
    return HttpResponse(unicode(request.get_user()))

def index(request):
    if request.method == 'POST':
        geotag_form = GeoTagAddForm(request.POST)
        if geotag_form.is_valid():
            geotag_form.save(request.get_user().get_profile())
    else:
        geotag_form = GeoTagAddForm()
    
    return render_to_response('index.html', RequestContext(request, {
        'photos': Photo.objects.all()[:6],
        'geotag_form': geotag_form,
        
    }))

def fetch_stream(request):
    data = get_next_photos_to_geotag.get_next_photos_to_geotag(request.get_user().get_profile().user, 4)
    return HttpResponse(json.dumps(data), mimetype="application/json")
