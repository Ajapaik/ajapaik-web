# encoding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages
from django.contrib.sites.models import Site
from django.http import HttpResponse
from django.utils import simplejson as json
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings

from django.core.files import File
from django.core.files.base import ContentFile

from project.models import Photo, City
from project.forms import GeoTagAddForm, CitySelectForm

import get_next_photos_to_geotag

def handle_uploaded_file(f):
    return ContentFile(f.read())
    
def photo_upload(request, photo_id):
    photo = get_object_or_404(Photo, pk=photo_id)
    if request.method == 'POST':    
        if 'user_file[]' in request.FILES.keys():
            for f in request.FILES.getlist('user_file[]'):
                fileobj = handle_uploaded_file(f)
                re_photo = Photo(
                    rephoto_of=photo,
                    city=photo.city,
                    user=request.get_user().get_profile()
                )
                re_photo.save()
                re_photo.image.save(f.name, fileobj)
                
    return HttpResponse('')

def logout(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('/')
    #return HttpResponse(unicode(request.get_user()))

def thegame(request):
    ctx = {}
    city_select_form = CitySelectForm(request.GET)
    if city_select_form.is_valid():
        ctx['city'] = City.objects.get(pk=city_select_form.cleaned_data['city'])
    
    return render_to_response('index.html', RequestContext(request, ctx))

def photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    site = Site.objects.get_current()
    
    template = ['', 'photo.html', 'photoview.html'][request.is_ajax() and 1 or 2]
    return render_to_response(template, RequestContext(request, {
        'photo': photo,
        'hostname': 'http://%s' % (site.domain, )
    }))

def frontpage(request):
    city_select_form = CitySelectForm()
    return render_to_response('frontpage.html', RequestContext(request, {
        'city_select_form': city_select_form,
        
    }))
    
def mapview(request):
    city_select_form = CitySelectForm(request.GET)
    city_id = city = None
    
    if city_select_form.is_valid():
        city_id = city_select_form.cleaned_data['city']
        city = City.objects.get(pk=city_id)
    else:
        city_select_form = CitySelectForm()
    
    data = get_next_photos_to_geotag.get_geotagged_photos(city_id)
    return render_to_response('mapview.html', RequestContext(request, {
        'json_data': json.dumps(data),
        'city': city,
        'city_select_form': city_select_form,
        
    }))    

def get_leaderboard(request):
    return HttpResponse(json.dumps(
        get_next_photos_to_geotag.get_leaderboard(request.get_user().get_profile().pk),
        mimetype="application/json"))

def geotag_add(request):
    data = request.POST
    is_correct, current_score, total_score, leaderboard_update, location_is_unclear = get_next_photos_to_geotag.submit_guess(request.get_user().get_profile(), data['photo_id'], data.get('lon'), data.get('lat'), hint_used=data.get('hint_used'))
    return HttpResponse(json.dumps({
        'is_correct': is_correct,
        'current_score': current_score,
        'total_score': total_score,
        'leaderboard_update': leaderboard_update,
    	'location_is_unclear': location_is_unclear,
    }), mimetype="application/json")

def leaderboard(request):
    leaderboard = get_next_photos_to_geotag.get_leaderboard(request.get_user().get_profile().pk)
    return render_to_response('block_leaderboard.html', RequestContext(request, {
        'leaderboard': leaderboard,
    }))
    

def fetch_stream(request):
    try:
        city = request.GET.get('city', None)
        city_id = int(city)
    except:
        city_id = None
        
    data = get_next_photos_to_geotag.get_next_photos_to_geotag(request.get_user().get_profile(), 4, city_id)
    return HttpResponse(json.dumps(data), mimetype="application/json")
