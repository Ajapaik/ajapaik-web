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

from project.models import Photo, City, Profile, Source
from project.forms import GeoTagAddForm, CitySelectForm
from sorl.thumbnail import get_thumbnail
from pprint import pprint
from django.db import models

import get_next_photos_to_geotag
import random
import datetime
import urllib

from django.forms.forms import Form
from django.forms.fields import ChoiceField

class FilterSpecCollection(object): # selectbox type, choice based
    def __init__(self, qs, params):
        self.qs = qs
        self.params = params
        self.filters = []
        self.filters_by_name = {}
        
    def register(self, filter_spec, field):
        filter_obj = filter_spec(self.params, field)
        self.filters.append(filter_obj)
        self.filters_by_name[filter_obj.get_slug_name()] = filter_obj
        
    def out(self):
        for f in self.filters:
            pass
    
    def get_filtered_qs(self):
        for item in self.filters:
            qs_filter = item.get_qs_filter()
            if qs_filter:
                self.qs = self.qs.filter(**dict(item.get_qs_filter()))
        return self.qs
    
    def get_form(self):
        class DynaForm(Form):
            def __init__(self, *args, **kwargs):
                args = list(args)
                filters = args.pop(0)
                
                super(DynaForm, self).__init__(*args, **kwargs)
                for item in filters:
                    choices = [(i['query_string'], i['display']) for i in list(item.choices())]
                    self.fields[item.get_slug_name()] = ChoiceField(choices=choices, label=item.get_label())
        
        initial = {}
        for item in self.filters:
            selected = [i['query_string'] for i in item.choices() if i['selected']] or ["",]
            initial[item.get_slug_name()] = selected.pop(0)
        
        return DynaForm(self.filters, initial=initial)

class FilterSpec(object):
    def get_qs_filter(self):
        for title, param_dict in self.links:
            if param_dict == self.selected_params:
                return self.selected_params
        return False
    
    def choices(self):
        for title, param_dict in self.links:
            yield {'selected': self.selected_params == param_dict,
                   'query_string': urllib.urlencode(param_dict),
                   'display': title
                   }
                                      
class DateFieldFilterSpec(FilterSpec):
    def __init__(self, params, field_path):
        self.field_path = field_path
        self.field_generic = '%s__' % field_path
        self.selected_params = dict([(k, v) for k, v in params.items() if k.startswith(self.field_generic)])
        
        today = datetime.date.today()
        one_week_ago = today - datetime.timedelta(days=7)
        one_month_ago = today - datetime.timedelta(days=30)
        today_str = today.strftime('%Y-%m-%d 23:59:59')
        
        self.links = (
            (_('All pictures'), {
                '%s__gte' % self.field_path: "",
                '%s__lte' % self.field_path: "",            
            }),
            (_('Added last week'), {
                '%s__gte' % self.field_path: one_week_ago.strftime('%Y-%m-%d'),
                '%s__lte' % self.field_path: today_str,
            }),
            (_('Added last month'), {
                '%s__gte' % self.field_path: one_month_ago.strftime('%Y-%m-%d'),
                '%s__lte' % self.field_path: today_str,
            }),
        )

    def get_slug_name(self):
        return u'creation_date_filter'

    def get_option_object(self):
        return None

    def get_label(self):
        return _('Vali vahemik')


class CityLookupFilterSpec(FilterSpec):
    def __init__(self, params, field_path):
        self.field_path = field_path
        self.field_generic = '%s__' % field_path
        self.selected_params = dict([(k, v) for k, v in params.items() if k.startswith(self.field_generic)])
        self.lookup = '%s__pk' % self.field_path
            
        self.links = []
        for city in City.objects.filter(lat__isnull=False, lon__isnull=False):
            self.links.append((city.name, {self.lookup: u'%s' % city.pk}))
        
        # Initial and default value
        if not self.get_qs_filter():
            self.selected_params = {self.lookup: u'%s' % settings.DEFAULT_CITY_ID}
        
    def get_option_object(self):
        return City.objects.get(**dict({"pk": self.selected_params[self.lookup]}))
    
    def get_slug_name(self):
        return u'city_lookup_filter'
    
    def get_label(self):
        return _('Vali linn')

class SourceLookupFilterSpec(FilterSpec):
    def __init__(self, params, field_path):
        self.field_path = field_path
        self.field_generic = '%s__' % field_path
        self.selected_params = dict([(k, v) for k, v in params.items() if k.startswith(self.field_generic)])
        self.lookup = '%s__eq' % self.field_path
            
        self.links = []
        self.links.append(('--', ''))
        for source in Source.objects.all():
            self.links.append((source.description, {self.lookup: u'%s' % source.pk}))
    
    def get_option_object(self):
        return Source.objects.get(**dict({"pk": self.selected_params[self.lookup]}))
    
    def get_slug_name(self):
        return u'source_lookup_filter'
    
    def get_label(self):
        return _('Vali allikas')

def handle_uploaded_file(f):
    return ContentFile(f.read())

def photo_upload(request, photo_id):
    photo = get_object_or_404(Photo, pk=photo_id)
    if request.method == 'POST':
        profile = request.get_user().get_profile()
        
        if 'fb_access_token' in request.POST:
            token = request.POST.get('fb_access_token')
            profile, fb_data = Profile.facebook.get_user(token)
            if profile is None:
                user = request.get_user() # will create user on-demand
                profile = user.get_profile()
                
                # update user info
                profile.update_from_fb_data(token, fb_data)
                
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
                    user=profile,
                    cam_scale_factor=data.get('scale_factor'),
                    cam_yaw=data.get('yaw'),
                    cam_pitch=data.get('pitch'),
                    cam_roll=data.get('roll'),
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

    site = Site.objects.get_current()
    ctx['hostname'] = 'http://%s' % (site.domain, )
    ctx['title'] = _('Guess the location')
    
    filters = FilterSpecCollection(None, request.GET)
    filters.register(CityLookupFilterSpec, 'city')
    #filters.register(DateFieldFilterSpec, 'created')
    #data = filters.get_filtered_qs().get_geotagged_photos_list()
    ctx['filters'] = filters
    
    return render_to_response('game.html', RequestContext(request, ctx))

def frontpage(request):
    try:
        example = random.choice(Photo.objects.filter(id__in=[2483, 2495, 2502, 3193, 3195, 3201, 3203, 3307], rephoto_of__isnull=False))
    except:
        example = random.choice(Photo.objects.filter(rephoto_of__isnull=False)[:8])
    example_source = Photo.objects.get(pk=example.rephoto_of.id)
    city_select_form = CitySelectForm(request.GET)
    
    if not city_select_form.is_valid():
        city_select_form = CitySelectForm()

    filters = FilterSpecCollection(None, request.GET)
    filters.register(CityLookupFilterSpec, 'city')
    filters_test = FilterSpecCollection(None, request.GET)
    filters_test.register(SourceLookupFilterSpec, 'source_id')
    
    return render_to_response('frontpage.html', RequestContext(request, {
        'city_select_form': city_select_form,
        'filters': filters,
        'filters_test': filters_test,
        'example': example,
        'example_source': example_source,
    }))

def photo_large(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    im = get_thumbnail(photo.image, '1024x1024', upscale=False)
    return redirect(im.url)

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
    
    if city:
        title = city.name +' - '+ _('Browse photos on map')
    else:
        title = _('Browse photos on map')

    qs = Photo.objects.all()
    
    filters = FilterSpecCollection(qs, request.GET)
    filters.register(CityLookupFilterSpec, 'city')
    filters.register(DateFieldFilterSpec, 'created')
    data = filters.get_filtered_qs().get_geotagged_photos_list()
    
    return render_to_response('mapview.html', RequestContext(request, {
        'json_data': json.dumps(data),
        'city': city,
        'title': title,
        'city_select_form': city_select_form,
        'filters': filters,
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
    qs = Photo.objects.all()
    filters = FilterSpecCollection(qs, request.GET)
    filters.register(DateFieldFilterSpec, 'created')
    filters.register(CityLookupFilterSpec, 'city')
    filters.register(SourceLookupFilterSpec, 'source_id')
    data = filters.get_filtered_qs().get_next_photos_to_geotag(request.get_user().get_profile(), 4)
    return HttpResponse(json.dumps(data), mimetype="application/json")
