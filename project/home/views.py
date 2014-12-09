# encoding: utf-8
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.sites.models import Site
from django.http import HttpResponse

from django.utils.translation import ugettext as _
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.core.exceptions import ObjectDoesNotExist
import hashlib

from project.home.models import Photo, City, Profile, Source, Device, DifficultyFeedback, GeoTag, FlipFeedback, UserMapView
from project.home.forms import CitySelectForm
from sorl.thumbnail import get_thumbnail
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True
from PIL.ExifTags import TAGS, GPSTAGS
from time import strftime, strptime
from StringIO import StringIO
from copy import deepcopy

import get_next_photos_to_geotag
import random
import datetime
import urllib
import json

from django.forms.forms import Form
from django.forms.fields import ChoiceField
from europeana import Search, BoundingBox


def _convert_to_degress(value):
	d0 = value[0][0]
	d1 = value[0][1]
	d = float(d0) / float(d1)

	m0 = value[1][0]
	m1 = value[1][1]
	m = float(m0) / float(m1)

	s0 = value[2][0]
	s1 = value[2][1]
	s = float(s0) / float(s1)

	return d + (m / 60.0) + (s / 3600.0)


def _get_exif_data(img):
	try:
		exif = img._getexif()
	except (AttributeError, IOError, KeyError, IndexError):
		exif = None
	if exif is None:
		return None

	exif_data = {}
	for (tag, value) in exif.items():
		decoded = TAGS.get(tag, tag)
		if decoded == "GPSInfo":
			for t in value:
				sub_decoded = GPSTAGS.get(t, t)
				exif_data[decoded + '.' + sub_decoded] = value[t]

		elif len(str(value)) < 50:
			exif_data[decoded] = value
		else:
			exif_data[decoded] = None

	return exif_data


class FilterSpecCollection(object):  # selectbox type, choice based
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
			if hasattr(item, "get_qs_exclude"):
				if item.get_qs_exclude():
					self.qs = self.qs.exclude(**dict(item.get_qs_exclude()))
			if hasattr(item, "get_qs_filter"):
				if item.get_qs_filter():
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
			selected = [i['query_string'] for i in item.choices() if i['selected']] or ["", ]
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
		return _('Choose range')


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
		return _('Choose city')


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
		return _('Choose source')


def handle_uploaded_file(f):
	return ContentFile(f.read())


def photo_upload(request, photo_id):
	photo = get_object_or_404(Photo, pk=photo_id)
	new_id = 0

	if request.method == 'POST':
		profile = request.get_user().profile
		if 'fb_access_token' in request.POST:
			token = request.POST.get('fb_access_token')
			profile, fb_data = Profile.facebook.get_user(token)
			if profile is None:
				user = request.get_user()
				profile = user.profile
				profile.update_from_fb_data(token, fb_data)
		latest_upload = Photo.objects.filter(rephoto_of=photo)
		previous_uploader = None
		if latest_upload:
			previous_uploader = latest_upload.values('user').order_by('-id')[:1].get()

		if 'user_file[]' in request.FILES.keys():
			for f in request.FILES.getlist('user_file[]'):
				if f.name.split()[-1] not in ["png", "PNG", "jpg", "JPG", "jpeg", "JPEG"]:
					pass
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
					cam_scale_factor=data.get('scale_factor', None),
					cam_yaw=data.get('yaw'),
					cam_pitch=data.get('pitch'),
					cam_roll=data.get('roll'),
				)
				if re_photo.cam_scale_factor:
					re_photo.cam_scale_factor = round(float(re_photo.cam_scale_factor), 6)
				re_photo.save()
				re_photo.image.save(f.name, fileobj)
				new_id = re_photo.pk

				img = Image.open(settings.MEDIA_ROOT + "/" + str(re_photo.image))
				exif_data = _get_exif_data(img)
				if exif_data:
					if 'GPSInfo.GPSLatitudeRef' in exif_data and 'GPSInfo.GPSLatitude' in exif_data and 'GPSInfo.GPSLongitudeRef' in exif_data and 'GPSInfo.GPSLongitude' in exif_data:
						gps_latitude_ref = exif_data.get('GPSInfo.GPSLatitudeRef')
						gps_latitude = exif_data.get('GPSInfo.GPSLatitude')
						gps_longitude_ref = exif_data.get('GPSInfo.GPSLongitudeRef')
						gps_longitude = exif_data.get('GPSInfo.GPSLongitude')

						lat = _convert_to_degress(gps_latitude)
						if gps_latitude_ref != "N":
							lat = 0 - lat

						lon = _convert_to_degress(gps_longitude)
						if gps_longitude_ref != "E":
							lon = 0 - lon

						re_photo.lat = lat
						re_photo.lon = lon
						re_photo.save()

					if 'Make' in exif_data or 'Model' in exif_data or 'LensMake' in exif_data or 'LensModel' in exif_data or 'Software' in exif_data:
						camera_make = exif_data.get('Make')
						camera_model = exif_data.get('Model')
						lens_make = exif_data.get('LensMake')
						lens_model = exif_data.get('LensModel')
						software = exif_data.get('Software')
						try:
							device = Device.objects.get(camera_make=camera_make, camera_model=camera_model,
														lens_make=lens_make, lens_model=lens_model, software=software)
						except ObjectDoesNotExist:
							device = Device(camera_make=camera_make, camera_model=camera_model, lens_make=lens_make,
											lens_model=lens_model, software=software)
							device.save()

						re_photo.device = device
						re_photo.save()

					if 'DateTimeOriginal' in exif_data:
						date_taken = exif_data.get('DateTimeOriginal')
						try:
							parsed_time = strptime(date_taken, "%Y:%m:%d %H:%M:%S")
						except ValueError:
							parsed_time = None
						if parsed_time:
							parsed_time = strftime("%H:%M:%S", parsed_time)

						# ignore default camera dates
						if parsed_time and parsed_time != '12:00:00' and parsed_time != '00:00:00':
							try:
								parsed_date = strptime(date_taken, "%Y:%m:%d %H:%M:%S")
							except ValueError:
								parsed_date = None
							if parsed_date:
								re_photo.date = strftime("%Y-%m-%d", parsed_date)
								re_photo.save()

				if re_photo.cam_scale_factor:
					new_size = tuple([int(x * re_photo.cam_scale_factor) for x in img.size])
					output_file = StringIO()

					if re_photo.cam_scale_factor < 1:
						x0 = (img.size[0] - new_size[0]) / 2
						y0 = (img.size[1] - new_size[1]) / 2
						x1 = img.size[0] - x0
						y1 = img.size[1] - y0
						new_img = img.transform(new_size, Image.EXTENT, (x0, y0, x1, y1))
						new_img.save(output_file, 'JPEG', quality=95)
						re_photo.image_unscaled = deepcopy(re_photo.image)
						re_photo.image.save(str(re_photo.image), ContentFile(output_file.getvalue()))
					elif re_photo.cam_scale_factor > 1:
						x0 = (new_size[0] - img.size[0]) / 2
						y0 = (new_size[1] - img.size[1]) / 2
						new_img = Image.new("RGB", new_size)
						new_img.paste(img, (x0, y0))
						new_img.save(output_file, 'JPEG', quality=95)
						re_photo.image_unscaled = deepcopy(re_photo.image)
						re_photo.image.save(str(re_photo.image), ContentFile(output_file.getvalue()))

			if previous_uploader and previous_uploader['user']:
				uploader = Profile.objects.get(pk=previous_uploader['user'])
				uploader.update_rephoto_score()

			profile.update_rephoto_score()

	return HttpResponse(json.dumps({'new_id': new_id}), content_type="application/json")


def logout(request):
	from django.contrib.auth import logout
	logout(request)
	return redirect(request.META['HTTP_REFERER'])


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
	ctx['filters'] = filters

	return render_to_response('game.html', RequestContext(request, ctx))


def frontpage(request):
	try:
		example = random.choice(Photo.objects.filter(
			id__in=[2483, 2495, 2502, 3193, 3195, 3201, 3203, 3307, 4821, 5485, 5535, 5588, 5617, 5644, 5645, 5646],
			rephoto_of__isnull=False))
	except ObjectDoesNotExist:
		example = random.choice(Photo.objects.filter(rephoto_of__isnull=False)[:8])
	example_source = Photo.objects.get(pk=example.rephoto_of.id)
	city_select_form = CitySelectForm(request.GET)

	if not city_select_form.is_valid():
		city_select_form = CitySelectForm()

	filters = FilterSpecCollection(None, request.GET)
	filters.register(CityLookupFilterSpec, 'city')

	return render_to_response('frontpage.html', RequestContext(request, {
		'city_select_form': city_select_form,
		'filters': filters,
		'example': example,
		'example_source': example_source,
	}))


def photo_large(request, photo_id):
	photo = get_object_or_404(Photo, id=photo_id)
	if photo.cam_scale_factor and photo.rephoto_of:
		# if rephoto is taken with mobile then make it same width/height as source photo
		im = get_thumbnail(photo.rephoto_of.image, '1024x1024', upscale=False)
		im = get_thumbnail(photo.image, str(im.width) + 'x' + str(im.height), crop="center")
	else:
		im = get_thumbnail(photo.image, '1024x1024', upscale=False)
	content = im.read()
	next_week = datetime.datetime.now() + datetime.timedelta(seconds=604800)
	response = HttpResponse(content, content_type='image/jpg')
	response['Content-Length'] = len(content)
	response['Cache-Control'] = "max-age=604800, public"  # 604800 = 7 days
	response['Expires'] = next_week.strftime("%a, %d %b %y %T GMT")
	return response


def photo_url(request, photo_id):
	photo = get_object_or_404(Photo, id=photo_id)
	if (photo.cam_scale_factor and photo.rephoto_of):
		# if rephoto is taken with mobile then make it same width/height as source photo
		im = get_thumbnail(photo.rephoto_of.image, '700x400')
		im = get_thumbnail(photo.image, str(im.width) + 'x' + str(im.height), crop="center")
	else:
		im = get_thumbnail(photo.image, '700x400')
	# return redirect(im.url)
	content = im.read()
	next_week = datetime.datetime.now() + datetime.timedelta(seconds=604800)
	response = HttpResponse(content, content_type='image/jpg')
	response['Content-Length'] = len(content)
	response['Cache-Control'] = "max-age=604800, public"  # 604800 = 7 days
	response['Expires'] = next_week.strftime("%a, %d %b %y %T GMT")
	return response


def photo_thumb(request, photo_id, thumb_size=None):
	cache_key = "ajapaik_pane_photo_thumb_response_%s" % photo_id
	cached_response = cache.get(cache_key)
	if cached_response:
		return cached_response
	p = get_object_or_404(Photo, id=photo_id)
	image_to_use = p.image_unscaled or p.image
	if image_to_use._get_width() >= image_to_use._get_height():
		thumb_str = "%d"
	else:
		thumb_str = "x%d"
	im = get_thumbnail(image_to_use, thumb_str % 150, crop="center")
	content = im.read()
	next_week = datetime.datetime.now() + datetime.timedelta(seconds=604800)
	response = HttpResponse(content, content_type='image/jpg')
	response['Content-Length'] = len(content)
	response['Cache-Control'] = "max-age=604800, public"
	response['Expires'] = next_week.strftime("%a, %d %b %y %T GMT")
	cache.set(cache_key, response)
	return response


def photo(request, photo_id):
	photo = get_object_or_404(Photo, id=photo_id)
	pseudo_slug = photo.get_pseudo_slug()
	# slug not needed if not enough data for slug or ajax request
	if pseudo_slug != "" and not request.is_ajax():
		return photoslug(request, photo.id, "")
	else:
		return photoslug(request, photo.id, pseudo_slug)

def _add_log_entry_if_necessary(user_profile, photo_id, user_action):
	existing_log_entry = None
	try:
		existing_log_entry = UserMapView.objects.filter(user_profile=user_profile, photo_id=photo_id, action=user_action)[:1].get()
	except ObjectDoesNotExist:
		if photo_id and user_action and not existing_log_entry:
			target_photo = Photo.objects.filter(id=photo_id)[:1].get()
			log_entry = UserMapView()
			log_entry.photo_id = photo_id
			log_entry.confidence = target_photo.confidence
			log_entry.action = user_action
			log_entry.user_profile = user_profile
			log_entry.save()

def heatmap_data(request):
	res = {}
	photo_id = request.GET.get("photo_id") or None
	if photo_id:
		target_photo = Photo.objects.filter(pk=photo_id).get()
		if hasattr(target_photo, "rephoto_of") and target_photo.rephoto_of is not None:
			target_photo = target_photo.rephoto_of
		if target_photo.lat and target_photo.lon:
			res["estimated_location"] = [target_photo.lat, target_photo.lon]
		res["heatmap_points"] = target_photo.get_heatmap_points()
	return HttpResponse(json.dumps(res), content_type="application/json")

def photoslug(request, photo_id, pseudo_slug):
	photo_obj = get_object_or_404(Photo, id=photo_id)
	user_profile = request.get_user().profile
	_add_log_entry_if_necessary(user_profile, photo_id, "opened_drawer")
	# redirect if slug in url doesn't match with our pseudo slug
	if photo_obj.get_pseudo_slug() != pseudo_slug:
		response = HttpResponse(content="", status=301)  # HTTP 301 for google juice
		response["Location"] = photo_obj.get_absolute_url()
		return response

	# switch places if rephoto url
	rephoto = None
	if hasattr(photo_obj, 'rephoto_of') and photo_obj.rephoto_of is not None:
		rephoto = photo_obj
		photo_obj = photo_obj.rephoto_of

	site = Site.objects.get_current()
	template = ['', 'block_photoview_bootstrap.html', 'photoview_bootstrap.html'][request.is_ajax() and 1 or 2]
	if not photo_obj.description:
		title = "Unknown photo"
	else:
		title = ' '.join(photo_obj.description.split(' ')[:5])[:50]
	return render_to_response(template, RequestContext(request, {
		'photo': photo_obj,
		'title': title,
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
	user_profile = request.get_user().profile
	_add_log_entry_if_necessary(user_profile, photo_id, "opened_heatmap")
	# redirect if slug in url doesn't match with our pseudo slug
	if photo_obj.get_pseudo_slug() != pseudo_slug:
		response = HttpResponse(content="", status=301)  # HTTP 301 for google juice
		response["Location"] = photo_obj.get_heatmap_url()
		return response

	# load heatmap data always from original photo
	if hasattr(photo_obj, 'rephoto_of') and photo_obj.rephoto_of is not None:
		photo_obj = photo_obj.rephoto_of

	data = get_next_photos_to_geotag.get_all_geotag_submits(photo_obj.id)
	if not photo_obj.description:
		title = "Unknown"
	else:
		title = ' '.join(photo_obj.description.split(' ')[:5])[:50] + ' - ' + _("Heat map")
	return render_to_response('heatmap.html', RequestContext(request, {
	'json_data': json.dumps(data),
	'city': photo_obj.city,
	'title': title,
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
	city = None
	get_params = request.GET.copy()
	city_id = get_params.get('city__pk', 0)

	if int(city_id) == 0:
		# backwards compatible with old city parameter
		city_id = get_params.get('city', 0)
		if int(city_id) > 0:
			get_params['city__pk'] = city_id

	if int(city_id) > 0:
		city = City.objects.get(pk=city_id)

	if city:
		title = city.name + ' - ' + _('Browse photos on map')
	else:
		title = _('Browse photos on map')

	qs = Photo.objects.all()

	filters = FilterSpecCollection(qs, get_params)
	filters.register(CityLookupFilterSpec, 'city')
	# filters.register(DateFieldFilterSpec, 'created')
	# filters.register(SourceLookupFilterSpec, 'source')
	data = filters.get_filtered_qs().get_geotagged_photos_list()
	photo_ids_user_has_looked_at = UserMapView.objects.filter(user_profile=request.get_user().profile).values_list('photo_id', flat=True)
	keys = {}
	for e in photo_ids_user_has_looked_at:
		keys[e] = 1
	photo_ids_user_has_looked_at = keys
	# data = filters.get_filtered_qs()

	leaderboard = get_next_photos_to_geotag.get_rephoto_leaderboard(request.get_user().profile.pk)

	return render_to_response('mapview.html', RequestContext(request, {
		'json_data': json.dumps(data),
		'city': city,
		'title': title,
		'filters': filters,
		'leaderboard': leaderboard,
	    'user_seen_photo_ids': photo_ids_user_has_looked_at,
	    'city_id': city_id
	}))


def get_leaderboard(request):
	return HttpResponse(json.dumps(
		get_next_photos_to_geotag.get_leaderboard(request.get_user().profile.pk)),
						content_type="application/json")


def geotag_add(request):
	data = request.POST
	is_correct, current_score, total_score, leaderboard_update, location_is_unclear, azimuth_false, azimuth_uncertain, heatmap_points, azimuth_tag_count, new_estimated_location = get_next_photos_to_geotag.submit_guess(
		request.get_user().profile, data.get('photo_id'), data.get('lon'), data.get('lat'),
		hint_used=data.get('hint_used'), azimuth=data.get('azimuth'), zoom_level=data.get('zoom_level'), azimuth_line_end_point=data.getlist('azimuth_line_end_point[]'))
	flip = data.get("flip", None)
	if flip is not None:
		flip_feedback = FlipFeedback()
		flip_feedback.photo_id = data['photo_id']
		flip_feedback.user_profile = request.get_user().profile
		if flip == "true":
			flip_feedback.flip = True
		elif flip == "false":
			flip_feedback.flip = False
		flip_feedback.save()

	return HttpResponse(json.dumps({
	'is_correct': is_correct,
	'current_score': current_score,
	'total_score': total_score,
	'leaderboard_update': leaderboard_update,
	'location_is_unclear': location_is_unclear,
	'azimuth_false': azimuth_false,
	'azimuth_uncertain': azimuth_uncertain,
	'heatmap_points': heatmap_points,
	'azimuth_tags': azimuth_tag_count,
	'new_estimated_location': new_estimated_location
	}), content_type="application/json")


def leaderboard(request):
	# leaderboard with first position, one in front of you, your score and one after you
	leaderboard = get_next_photos_to_geotag.get_leaderboard(request.get_user().profile.pk)
	template = ['', 'block_leaderboard.html', 'leaderboard.html'][request.is_ajax() and 1 or 2]
	return render_to_response(template, RequestContext(request, {
	'leaderboard': leaderboard,
	'title': _('Leaderboard'),
	}))


def top50(request):
	# leaderboard with top 50 scores
	leaderboard = get_next_photos_to_geotag.get_leaderboard50(request.get_user().profile.pk)
	template = ['', 'block_leaderboard.html', 'leaderboard.html'][request.is_ajax() and 1 or 2]
	return render_to_response(template, RequestContext(request, {
	'leaderboard': leaderboard,
	'title': _('Leaderboard'),
	}))


def rephoto_top50(request):
	# leaderboard with top 50 scores
	leaderboard = get_next_photos_to_geotag.get_rephoto_leaderboard50(request.get_user().profile.pk)
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
	filters.register(SourceLookupFilterSpec, 'source')
	# filters.register(UserAlreadyGeotaggedFilterSpec, request.get_user().profile.pk)
	data = {}
	data["photos"], data["user_seen_all"], data[
		"nothing_more_to_show"] = filters.get_filtered_qs().get_next_photo_to_geotag(request)
	return HttpResponse(json.dumps(data), content_type="application/json")


def difficulty_feedback(request):
	# TODO: Tighten down security when it becomes apparent people are abusing this

	user_profile = request.get_user().profile
	user_trustworthiness = get_next_photos_to_geotag.calc_trustworthiness(user_profile.pk)
	user_last_geotag = GeoTag.objects.filter(user=user_profile).order_by("-created")[:1].get()
	level = request.POST.get("level") or None
	photo_id = request.POST.get("photo_id") or None
	if user_profile and level and photo_id:
		feedback_object = DifficultyFeedback()
		feedback_object.user_profile = user_profile
		feedback_object.level = level
		feedback_object.photo_id = photo_id
		feedback_object.trustworthiness = user_trustworthiness
		feedback_object.geotag = user_last_geotag
		feedback_object.save()
	photo = Photo.objects.filter(id=photo_id)[:1].get()
	photo.set_calculated_fields()
	return HttpResponse("OK")

def log_user_map_action(request):
	user_profile = request.get_user().profile
	photo_id = request.POST.get("photo_id") or None
	user_action = request.POST.get("user_action") or None
	_add_log_entry_if_necessary(user_profile, photo_id, user_action)
	return HttpResponse("OK")


def custom_404(request):
	response = render_to_response('404.html', {}, context_instance=RequestContext(request))
	response.status_code = 404
	return response


def custom_500(request):
	response = render_to_response('500.html', {}, context_instance=RequestContext(request))
	response.status_code = 500
	return response


def europeana(request):
	# This is for testing Europeana integration, nothing good yet
	x1 = request.GET.get("x1", None)
	x2 = request.GET.get("x2", None)
	y1 = request.GET.get("y1", None)
	y2 = request.GET.get("y2", None)
	bounding_box = None
	if x1 and x2 and y1 and y2:
		bounding_box = BoundingBox(x1, y1, x2, y2)
	results = Search().query(request.GET.get("query", "Kose"), request.GET.get("refinement_terms", None), bounding_box,
							 request.GET.get("start", 1), request.GET.get("size", 12))
	return render_to_response("europeana.html", RequestContext(request, {
		'results': results
	}))

@login_required
@user_passes_test(lambda u: u.groups.filter(name="csv_uploaders").count() == 0, login_url="/admin/")
def csv_upload(request):
	import csv, zipfile, hashlib
	csv_file = request.FILES["csv_file"]
	dialect = csv.Sniffer().sniff(csv_file.read(1024), delimiters=";,")
	header_row = None
	photos_metadata = {}
	for row in csv.reader(csv_file, dialect):
		if not header_row:
			header_row = row
			continue
		row = dict(zip(header_row, row))
		photos_metadata[row.get("image")] = row

	zip_file = zipfile.ZipFile(request.FILES["zip_file"])

	for key in photos_metadata.keys():
		try:
			image_file = zip_file.read(key)
		except KeyError:
			continue
		meta_for_this_image = photos_metadata[key]
		source_key = meta_for_this_image.get("number") or key
		try:
			existing_photo = Photo.objects.get(source_key=source_key)
			continue
		except ObjectDoesNotExist:
			pass
		extension = key.split(".")[-1]
		upload_file_name = "uploads/%s.%s" %(hashlib.md5(key).hexdigest(), extension)
		fout = open("/var/garage/" + upload_file_name, "w")
		fout.write(image_file)
		fout.close()
		place_name = meta_for_this_image.get("place") or "Ajapaik"
		try:
			city = City.objects.get(name=place_name)
		except ObjectDoesNotExist:
			city = City(name=place_name)
			city.save()
		description='; '.join(filter(None, [meta_for_this_image[sub_key].strip() for sub_key in ('description','title') if sub_key in meta_for_this_image]))
		source_name = meta_for_this_image.get("institution") or "Ajapaik"
		try:
			source = Source.objects.get(description=source_name)
		except ObjectDoesNotExist:
			source=Source(name=source_name, description=source_name)
			source.save()
		source_url = meta_for_this_image.get("url")
		p = Photo(date_text=meta_for_this_image.get("date"), city=city, description=description, source=source, source_url=source_url, source_key=source_key)
		p.image.name = upload_file_name
		p.save()
	return HttpResponse("OK")

def public_photo_upload(request):
	all_cities = City.objects.all()
	return render_to_response('photo_upload.html', RequestContext(request, {
		'cities': all_cities
	}))

def public_photo_upload_handler(request):
	user_profile = request.get_user().profile
	uploaded_photos = request.FILES.getlist('files[]')
	city_id = request.POST.get('city')
	ret = {"files": []}
	for each in uploaded_photos:
		p = Photo()
		p.image = each
		p.city_id = city_id
		p.save()
		ret["files"].append({"name": p.image.name})

	# {"files": [
	# {
	# "name": "picture1.jpg",
	# "size": 902604,
	# "url": "http:\/\/example.org\/files\/picture1.jpg",
	# "thumbnailUrl": "http:\/\/example.org\/files\/thumbnail\/picture1.jpg",
	# "deleteUrl": "http:\/\/example.org\/files\/picture1.jpg",
	# "deleteType": "DELETE"
	# },
	# {
	# "name": "picture2.jpg",
	# "size": 841946,
	# "url": "http:\/\/example.org\/files\/picture2.jpg",
	# "thumbnailUrl": "http:\/\/example.org\/files\/thumbnail\/picture2.jpg",
	# "deleteUrl": "http:\/\/example.org\/files\/picture2.jpg",
	# "deleteType": "DELETE"
	# }
	# ]}
	return HttpResponse(json.dumps(ret), content_type="application/json")

def pane_contents(request):
	marker_ids = request.POST.getlist('marker_ids[]')
	data = []
	for p in Photo.objects.filter(confidence__gte=0.3, lat__isnull=False, lon__isnull=False, rephoto_of__isnull=True, id__in=marker_ids):
		rephoto_count = len(list(Photo.objects.filter(rephoto_of=p.id)))
		im_url = reverse('project.home.views.photo_thumb', args=(p.id,))
		try:
			if p.image._get_width() >= p.image._get_height():
				thumb_str = "%d"
			else:
				thumb_str = "x%d"
			im = get_thumbnail(p.image, thumb_str % 150, crop="center")
			data.append([p.id, im_url, rephoto_count, p.flip, p.description, p.azimuth, im._size[0], im._size[1]])
		except IOError:
			pass
	return render_to_response('pane_contents.html', RequestContext(request, {"data": data}))


def grid(request):
	qs = Photo.objects.all()
	get_params = request.GET.copy()
	city_id = get_params.get('city__pk', 1)
	filters = FilterSpecCollection(qs, get_params)
	filters.register(CityLookupFilterSpec, 'city')
	data = filters.get_filtered_qs().get_old_photos_for_grid_view(0, settings.GRID_VIEW_PAGE_SIZE)
	photo_count = filters.get_filtered_qs().get_old_photo_count_for_grid_view()
	return render_to_response('grid_bootstrap.html', RequestContext(request, {
		"data": data,
	    "photo_count": photo_count,
		"city_id": city_id,
		"start": 0,
	    "filters": filters,
		"page_size": settings.GRID_VIEW_PAGE_SIZE
	}))


def grid_infinite_scroll(request):
	qs = Photo.objects.all()
	get_params = request.GET.copy()
	filters = FilterSpecCollection(qs, get_params)
	filters.register(CityLookupFilterSpec, 'city')
	start = int(get_params['start'])
	data = filters.get_filtered_qs().get_old_photos_for_grid_view(start, start + settings.GRID_VIEW_PAGE_SIZE)
	return HttpResponse(json.dumps(data), content_type="application/json")
