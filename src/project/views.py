# encoding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
from django.utils import simplejson as json
from django.shortcuts import redirect

from project.models import Photo
from project.forms import GeoTagAddForm

import get_next_photos_to_geotag

def logout(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('/')
    #return HttpResponse(unicode(request.get_user()))

def thegame(request):
#     if request.method == 'POST':
#         geotag_form = GeoTagAddForm(request.POST)
#         if geotag_form.is_valid():
#             geotag_form.save(request.get_user().get_profile())
#     else:
#         geotag_form = GeoTagAddForm()
    
    return render_to_response('index.html', RequestContext(request, {
#         'geotag_form': geotag_form,
        
    }))

def frontpage(request):
    return render_to_response('frontpage.html', RequestContext(request, {
        
    }))
    
def mapview(request):
    data = get_next_photos_to_geotag.get_geotagged_photos()
    return render_to_response('mapview.html', RequestContext(request, {
        'json_data': json.dumps(data),
        
    }))    

def geotag_add(request):
    data = request.GET
    is_correct, current_score, total_score = get_next_photos_to_geotag.submit_guess(request.get_user().get_profile(), data['photo_id'], data.get('lon'), data.get('lat'))
    return HttpResponse(json.dumps({
        'is_correct': is_correct,
        'current_score': current_score,
        'total_score': total_score,
    }), mimetype="application/json")

def fetch_stream(request):
    data = get_next_photos_to_geotag.get_next_photos_to_geotag(request.get_user().get_profile(), 4)
    return HttpResponse(json.dumps(data), mimetype="application/json")
