# encoding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages
from django.contrib.sites.models import Site
from django.http import HttpResponse
from django.utils import simplejson as json
from django.utils.translation import ugettext as _
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings

from django.core.files import File
from django.core.files.base import ContentFile

from project.models import Photo, City
from project.forms import GeoTagAddForm, CitySelectForm
from sorl.thumbnail import get_thumbnail
from pprint import pprint

import get_next_photos_to_geotag

def handle_uploaded_file(f):
    return ContentFile(f.read())
    
def photo_upload(request, photo_id):
    photo = get_object_or_404(Photo, pk=photo_id)
    if request.method == 'POST':    
        if 'user_file[]' in request.FILES.keys():
            for f in request.FILES.getlist('user_file[]'):
                fileobj = handle_uploaded_file(f)
                data = request.POST
                re_photo = Photo(
                    rephoto_of=photo,
                    city=photo.city,
                    description=data.get('description', photo.description),
                    lat=data.get('lat', None),
                    lon=data.get('lon', None),
                    date_text=data.get('date_text', None),
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

    ctx['title'] = _('Guess the location')
    return render_to_response('game.html', RequestContext(request, ctx))

def frontpage(request):
    city_select_form = CitySelectForm(request.GET)
    
    if not city_select_form.is_valid():
        city_select_form = CitySelectForm()

    return render_to_response('frontpage.html', RequestContext(request, {
        'city_select_form': city_select_form,
        
    }))

def photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    rephoto = None
    if hasattr(photo, 'rephoto_of') and photo.rephoto_of is not None:
        rephoto = photo
        photo = photo.rephoto_of
    site = Site.objects.get_current()
    
    template = ['', 'block_photoview.html', 'photoview.html'][request.is_ajax() and 1 or 2]
    return render_to_response(template, RequestContext(request, {
        'photo': photo,
        'title': ' '.join(photo.description.split(' ')[:6])[:50],
        'description': photo.description,
        'rephoto': rephoto,
        'hostname': 'http://%s' % (site.domain, )
    }))

def photoview(request, slug):
    photo_obj = get_object_or_404(Photo, slug=slug)
    return photo(request, photo_obj.id)

def photo_url(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    im = get_thumbnail(photo.image, '700x400')
    return redirect(im.url)

def photo_thumb(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    im = get_thumbnail(photo.image, '50x50', crop='center')
    return redirect(im.url)

def photo_heatmap(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    if hasattr(photo, 'rephoto_of') and photo.rephoto_of is not None:
        photo = photo.rephoto_of
    data = get_next_photos_to_geotag.get_all_geotag_submits(photo.id)
    return render_to_response('heatmap.html', RequestContext(request, {
        'json_data': json.dumps(data),
        'city': photo.city,
        'title': ' '.join(photo.description.split(' ')[:6])[:50] +' - '+ _("Heat map"),
        'description': photo.description,
        'photo_lon': photo.lon,
        'photo_lat': photo.lat,
    }))

def photoview_heatmap(request, slug):
    photo_obj = get_object_or_404(Photo, slug=slug)
    return photo_heatmap(request, photo_obj.id)

def heatmap(request):
    city_select_form = CitySelectForm(request.GET)
    city_id = city = None
    
    if city_select_form.is_valid():
        city_id = city_select_form.cleaned_data['city']
        city = City.objects.get(pk=city_id)
    else:
        city_select_form = CitySelectForm()
    
    data = get_next_photos_to_geotag.get_all_geotagged_photos(city_id)
    return render_to_response('heatmap.html', RequestContext(request, {
        'json_data': json.dumps(data),
        'city': city,
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
        'title': _('Browse photos on map'),
        'city_select_form': city_select_form,
        
    }))

def get_leaderboard(request):
    return HttpResponse(json.dumps(
        get_next_photos_to_geotag.get_leaderboard(request.get_user().get_profile().pk)),
        mimetype="application/json")

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
    template = ['', 'block_leaderboard.html', 'leaderboard.html'][request.is_ajax() and 1 or 2]
    return render_to_response(template, RequestContext(request, {
        'leaderboard': leaderboard,
        'title': _('Leaderboard'),
    }))

def top50(request):
    leaderboard = get_next_photos_to_geotag.get_leaderboard50(request.get_user().get_profile().pk)
    template = ['', 'block_leaderboard.html', 'leaderboard.html'][request.is_ajax() and 1 or 2]
    return render_to_response(template, RequestContext(request, {
        'leaderboard': leaderboard,
        'title': _('Leaderboard'),
    }))

def fetch_stream(request):
    try:
        city = request.GET.get('city', None)
        city_id = int(city)
    except:
        city_id = None
        
    data = get_next_photos_to_geotag.get_next_photos_to_geotag(request.get_user().get_profile(), 4, city_id)
    return HttpResponse(json.dumps(data), mimetype="application/json")
