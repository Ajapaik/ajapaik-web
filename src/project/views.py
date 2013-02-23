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

def photo_url(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    im = get_thumbnail(photo.image, '700x400')
    return redirect(im.url)

def photo_thumb(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    im = get_thumbnail(photo.image, '50x50', crop='center')
    return redirect(im.url)

def photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    pseudo_slug = photo.get_pseudo_slug()
    # slug not needed if not enough data for slug or ajax request
    if pseudo_slug != "" and not request.is_ajax():
        return photoslug(request, photo.id, "")
    else:
        return photoslug(request, photo.id, pseudo_slug)

def photoslug(request, photo_id, pseudo_slug):
    photo_obj = get_object_or_404(Photo, id=photo_id)
    # redirect if slug in url doesn't match with our pseudo slug
    if photo_obj.get_pseudo_slug() != pseudo_slug:
        response = HttpResponse(content="", status=301) # HTTP 301 for google juice
        response["Location"] = photo_obj.get_absolute_url()
        return response

    # switch places if rephoto url
    rephoto = None
    if hasattr(photo_obj, 'rephoto_of') and photo_obj.rephoto_of is not None:
        rephoto = photo_obj
        photo_obj = photo_obj.rephoto_of

    site = Site.objects.get_current()
    template = ['', 'block_photoview.html', 'photoview.html'][request.is_ajax() and 1 or 2]
    return render_to_response(template, RequestContext(request, {
        'photo': photo_obj,
        'title': ' '.join(photo_obj.description.split(' ')[:5])[:50],
        'description': photo_obj.description,
        'rephoto': rephoto,
        'hostname': 'http://%s' % (site.domain, )
    }))

def photo_heatmap(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    pseudo_slug = photo.get_pseudo_slug()
    # slug not needed if not enough data for slug or ajax request
    if pseudo_slug != "" and not request.is_ajax():
        return photoslug_heatmap(request, photo.id, "")
    else:
        return photoslug_heatmap(request, photo.id, pseudo_slug)


def photoslug_heatmap(request, photo_id, pseudo_slug):
    photo_obj = get_object_or_404(Photo, id=photo_id)
    # redirect if slug in url doesn't match with our pseudo slug
    if photo_obj.get_pseudo_slug() != pseudo_slug:
        response = HttpResponse(content="", status=301) # HTTP 301 for google juice
        response["Location"] = photo_obj.get_heatmap_url()
        return response

    # load heatmap data always from original photo
    if hasattr(photo_obj, 'rephoto_of') and photo_obj.rephoto_of is not None:
        photo_obj = photo_obj.rephoto_of

    data = get_next_photos_to_geotag.get_all_geotag_submits(photo_obj.id)
    return render_to_response('heatmap.html', RequestContext(request, {
        'json_data': json.dumps(data),
        'city': photo_obj.city,
        'title': ' '.join(photo_obj.description.split(' ')[:5])[:50] +' - '+ _("Heat map"),
        'description': photo_obj.description,
        'photo_lon': photo_obj.lon,
        'photo_lat': photo_obj.lat,
    }))

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
    # leaderboard with first position, one in front of you, your score and one after you
    leaderboard = get_next_photos_to_geotag.get_leaderboard(request.get_user().get_profile().pk)
    template = ['', 'block_leaderboard.html', 'leaderboard.html'][request.is_ajax() and 1 or 2]
    return render_to_response(template, RequestContext(request, {
        'leaderboard': leaderboard,
        'title': _('Leaderboard'),
    }))

def top50(request):
    # leaderboard with top 50 scores
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
