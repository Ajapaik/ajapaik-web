from PIL import Image
from django.core.files import File
from django.db import models
from django.db.models import Count, Sum
from operator import attrgetter

from django.contrib.auth.models import User as BaseUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

# from filebrowser.fields import FileBrowseField
from django_extensions.db.fields import json
from django.template.defaultfilters import slugify
from django.db.models import Q

from urllib2 import urlopen
from contextlib import closing
import urllib
from django.utils.simplejson import loads as json_decode
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from oauth2client.django_orm import FlowField
from oauth2client.django_orm import CredentialsField

from sorl.thumbnail import get_thumbnail
from sorl.thumbnail import ImageField

import math
import datetime
import random

# Create profile automatically
def user_post_save(sender, instance, **kwargs):
	profile, new = Profile.objects.get_or_create(user=instance)


def distance_in_meters(lon1, lat1, lon2, lat2):
	if not lon1 or not lat1 or not lon2 or not lat2:
		return None
	lat_coeff = math.cos(math.radians((lat1 + lat2) / 2.0))
	return (2 * 6350e3 * 3.1415 / 360) * math.sqrt((lat1 - lat2) ** 2 + ((lon1 - lon2) * lat_coeff) ** 2)

models.signals.post_save.connect(user_post_save, sender=BaseUser)

class City(models.Model):
	name = models.TextField()
	lat = models.FloatField(null=True)
	lon = models.FloatField(null=True)

	class Meta:
		app_label = "project"

	def __unicode__(self):
		return u'%s' % self.name


class Album(models.Model):
	FRONTPAGE, FAVORITES, COLLECTION = range(3)
	TYPE_CHOICES = (
	(FRONTPAGE, 'Frontpage'),
	(FAVORITES, 'Favorites'),
	(COLLECTION, 'Collection'),
	)
	name = models.CharField(max_length=255)
	slug = models.SlugField()
	description = models.TextField(null=True, blank=True)

	atype = models.PositiveSmallIntegerField(choices=TYPE_CHOICES)
	profile = models.ForeignKey('Profile', related_name='albums', blank=True, null=True)

	is_public = models.BooleanField(default=True)

	photos = models.ManyToManyField('Photo', through='AlbumPhoto', related_name='albums')

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	class Meta:
		app_label = "project"


class AlbumPhoto(models.Model):
	album = models.ForeignKey('Album')
	photo = models.ForeignKey('Photo')
	sort_order = models.PositiveSmallIntegerField(default=0)
	created = models.DateTimeField(auto_now_add=True)
	notes = models.TextField(null=True, blank=True)

	class Meta:
		app_label = "project"


class PhotoManager(models.Manager):
	def get_query_set(self):
		return self.model.QuerySet(self.model)


import uuid
def get_unique_image_file_name(filename):
	ext = filename.split('.')[-1]
	filename = "%s.%s" % (uuid.uuid4(), ext)
	return filename


class Photo(models.Model):
	objects = PhotoManager()

	id = models.AutoField(primary_key=True)
	#Removed sorl ImageField because of https://github.com/mariocesar/sorl-thumbnail/issues/295
	image = models.ImageField(upload_to=lambda instance, filename: 'uploads/{0}'.format(get_unique_image_file_name(filename)), blank=True, null=True)
	image_unscaled = models.ImageField(upload_to=lambda instance, filename: 'uploads/{0}'.format(get_unique_image_file_name(filename)), blank=True, null=True)
	flip = models.NullBooleanField()
	date = models.DateField(null=True, blank=True)
	date_text = models.CharField(max_length=100, blank=True, null=True)
	description = models.TextField(null=True, blank=True)

	user = models.ForeignKey('Profile', related_name='photos', blank=True, null=True)

	level = models.PositiveSmallIntegerField(default=0)
	guess_level = models.FloatField(null=True, blank=True)

	lat = models.FloatField(null=True, blank=True)
	lon = models.FloatField(null=True, blank=True)
	bounding_circle_radius = models.FloatField(null=True, blank=True)
	azimuth = models.FloatField(null=True, blank=True)
	confidence = models.FloatField(default=0)
	azimuth_confidence = models.FloatField(default=0)

	source_key = models.CharField(max_length=100, null=True, blank=True)
	source_url = models.URLField(null=True, blank=True)
	source = models.ForeignKey('Source', null=True, blank=True)
	device = models.ForeignKey('Device', null=True, blank=True)

	city = models.ForeignKey('City', related_name='cities')
	rephoto_of = models.ForeignKey('self', blank=True, null=True, related_name='rephotos')

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	#scale_factor: vana pildi zoom level pildistamise hetkel (float; vahemikus [0.5, 4.0])
	#yaw, pitch, roll: telefoni orientatsioon pildistamise hetkel (float; radiaanides)
	cam_scale_factor = models.FloatField(null=True, blank=True)
	cam_yaw = models.FloatField(null=True, blank=True)
	cam_pitch = models.FloatField(null=True, blank=True)
	cam_roll = models.FloatField(null=True, blank=True)

	class Meta:
		ordering = ['-id']
		app_label = "project"

	class QuerySet(models.query.QuerySet):
		def get_geotagged_photos_list(self):
			rephotographed_ids = self.filter(
				rephoto_of__isnull=False).order_by(
				'rephoto_of').values_list(
				'rephoto_of', flat=True)
			filtered_rephotos = self.filter(
				rephoto_of__isnull=False).order_by(
				'rephoto_of', '-id').distinct(
				'rephoto_of').filter(
				rephoto_of__in=rephotographed_ids)
			filtered_rephotos_ids = []
			for p in filtered_rephotos:
				filtered_rephotos_ids.append(p.rephoto_of.id)
			zipped_rephotos = zip(filtered_rephotos_ids, filtered_rephotos)
			rephotos = dict(zipped_rephotos)
			#return len(rephotographed_ids), len(filtered_rephotos), len(filtered_rephotos_ids), len(zipped_rephotos), len(rephotos)
			data = []
			for p in self.filter(confidence__gte=0.3,
								 lat__isnull=False, lon__isnull=False,
								 rephoto_of__isnull=True):
				r = rephotos.get(p.id)
				if r is not None and bool(r.image):
					#im = get_thumbnail(r.image, '50x50', crop='center')
					im_url = reverse('views.photo_thumb', args=(r.id,))
				else:
					#im = get_thumbnail(p.image, '50x50', crop='center')
					im_url = reverse('views.photo_thumb', args=(p.id,))
				data.append((p.id, im_url, p.lon, p.lat, p.id, p.flip in rephotographed_ids))
			return data

		@staticmethod
		def _get_game_json_format_photo(photo, distance_from_last):
			# TODO: proper JSON serialization
			if not distance_from_last:
				distance_from_last = "Unknown"
			from get_next_photos_to_geotag import _make_thumbnail, _make_fullscreen
			assert isinstance(photo, Photo)
			return {
				"id": photo.id,
				"description": photo.description,
				"date_text": photo.date_text,
				"source_key": photo.source_key,
				"flip": photo.flip,
				"big": _make_thumbnail(photo, "700x400"),
				"large": _make_fullscreen(photo),
				"confidence": photo.confidence,
				"distance_from_last": distance_from_last
			}

		def get_next_photo_to_geotag(self, request):
			user_id = request.get_user().get_profile().pk
			from get_next_photos_to_geotag import calc_trustworthiness

			user_trustworthiness = calc_trustworthiness(user_id)

			city_photos_set = self.filter(rephoto_of_id=None)
			city_photo_ids = frozenset([p.id for p in city_photos_set])

			user_geotags_in_city = GeoTag.objects.filter(user=user_id, photo_id__in=city_photo_ids)
			user_skips_in_city = Skip.objects.filter(user=user_id, photo_id__in=city_photo_ids)
			user_last_action = None
			user_last_interacted_photo = None
			distance_between_photos = None
			user_last_geotag = None
			user_last_skip = None
			if len(user_geotags_in_city) > 0:
				user_last_geotag = user_geotags_in_city.order_by("-created")[0]
			if len(user_skips_in_city) > 0:
				user_last_skip = user_skips_in_city.order_by("-created")[0]
			if user_last_skip and user_last_geotag and user_last_skip.created > user_last_geotag.created:
				user_last_action = user_last_skip
			else:
				user_last_action = user_last_geotag
			if user_last_action is not None:
				try:
					user_last_interacted_photo = city_photos_set.filter(id=user_last_action.photo_id, lat__isnull=False, lon__isnull=False)[:1].get()
				except:
					user_last_interacted_photo = None

			user_geotagged_photo_ids = list(set(user_geotags_in_city.values_list("photo_id", flat=True)))
			# TODO: Tidy up
			user_skipped_photo_ids = list(set(list(user_skips_in_city.values_list("photo_id", flat=True))) - set(list(user_geotags_in_city.values_list("photo_id", flat=True))))
			user_has_seen_photo_ids = set(user_geotagged_photo_ids + user_skipped_photo_ids)

			user_seen_all = False
			nothing_more_to_show = False

			if "user_skip_array" not in request.session:
				request.session.user_skip_array = []

			if user_trustworthiness < 0.4:
				# Novice users should only receive the easiest images to prove themselves
				ret = city_photos_set.exclude(id__in=user_has_seen_photo_ids).order_by("-guess_level", "-confidence")
				if len(ret) == 0:
					# If the user has seen all the photos, offer something at random
					user_seen_all = True
					ret = city_photos_set.order_by("-guess_level", "-confidence")
			else:
				# Let's try to show the more experienced users photos they have not yet seen at all
				ret = city_photos_set.exclude(id__in=user_has_seen_photo_ids)
				if len(ret) == 0:
					# If the user has seen them all, let's try showing her photos she has skipped (but not in this session) or not marked an azimuth on
					user_seen_all = True
					user_geotags_without_azimuth_in_city = user_geotags_in_city.exclude(azimuth__isnull=False)
					user_geotagged_without_azimuth_photo_ids = list(set(user_geotags_without_azimuth_in_city.values_list("photo_id", flat=True)))
					ret = city_photos_set.filter(id__in=(user_geotagged_without_azimuth_photo_ids + user_skipped_photo_ids)).exclude(id__in=request.session.user_skip_array)
					if len(ret) == 0:
						# This user has geotagged all the city's photos with azimuths, show her photos that have low confidence or don't have a correct geotag from her
						user_incorrect_geotags = user_geotags_in_city.filter(is_correct=False)
						user_correct_geotags = user_geotags_in_city.filter(is_correct=True)
						user_incorrectly_geotagged_photo_ids = set(user_incorrect_geotags.values_list("photo_id", flat=True))
						user_correctly_geotagged_photo_ids = set(user_correct_geotags.values_list("photo_id", flat=True))
						user_no_correct_geotags_photo_ids = list(user_incorrectly_geotagged_photo_ids - user_correctly_geotagged_photo_ids)
						ret = city_photos_set.filter(Q(confidence__lt=0.3) | Q(id__in=user_no_correct_geotags_photo_ids))
						if len(ret) == 0:
							nothing_more_to_show = True
				good_candidates = []
				shitty_candidates = []
				if user_trustworthiness < 0.4:
					for p in ret:
						distance_from_last = 99999
						if user_last_interacted_photo:
							distance_from_last = distance_in_meters(p.lon, p.lat, user_last_interacted_photo.lon, user_last_interacted_photo.lat)
						if p.confidence > 0.7 and 250 <= distance_from_last <= 1000:
							good_candidates.append(p)
						elif p.confidence > 0.7:
							shitty_candidates.append(p)
				elif 0.4 <= user_trustworthiness < 0.7:
					for p in ret:
						distance_from_last = 99999
						if user_last_interacted_photo:
							distance_from_last = distance_in_meters(p.lon, p.lat, user_last_interacted_photo.lon, user_last_interacted_photo.lat)
						if 0.4 <= p.confidence <= 0.7 and 250 <= distance_from_last <= 1000:
							good_candidates.append(p)
						elif 0.4 <= p.confidence <= 0.7:
							shitty_candidates.append(p)
				else:
					for p in ret:
						distance_from_last = 99999
						if user_last_interacted_photo:
							distance_from_last = distance_in_meters(p.lon, p.lat, user_last_interacted_photo.lon, user_last_interacted_photo.lat)
						if p.confidence < 0.4 and 250 <= distance_from_last <= 1000:
							good_candidates.append(p)
						elif p.confidence < 0.4:
							shitty_candidates.append(p)
				if len(good_candidates) > 0:
					ret = good_candidates
				else:
					ret = shitty_candidates
			if ret and ret[0].id in user_skipped_photo_ids:
				request.session.user_skip_array.append(ret[0].id)
			if len(ret) == 0:
				return [{}], True, True
			return [self._get_game_json_format_photo(ret[0], distance_between_photos)], user_seen_all, nothing_more_to_show


	def flip_horizontal(self):
		image = Image.open(self.image.path)
		exif = image.info['exif']
		image = image.transpose(Image.FLIP_LEFT_RIGHT)
		image.save(self.image.path, File(image), exif=exif)

	def __unicode__(self):
		return u'%s - %s (%s) (%s)' % (self.id, self.description, self.date_text, self.source_key)

	@models.permalink
	def get_detail_url(self):
		return ('views.photo', [self.id, ])

	@models.permalink
	def get_absolute_url(self):
		pseudo_slug = self.get_pseudo_slug();
		if pseudo_slug != "":
			return ('views.photoslug', [self.id, pseudo_slug, ])
		else:
			return ('views.photo', [self.id, ])

	@models.permalink
	def get_heatmap_url(self):
		pseudo_slug = self.get_pseudo_slug();
		if pseudo_slug != "":
			return ('views.photoslug_heatmap', [self.id, pseudo_slug, ])
		else:
			return ('views.photo_heatmap', [self.id, ])

	def get_pseudo_slug(self):
		slug = ""
		if self.description is not None and self.description != "":
			slug = "-".join(slugify(self.description).split('-')[:6])[:60]
		elif self.source_key is not None and self.source_key != "":
			slug = slugify(self.source_key)
		else:
			slug = slugify(self.created.__format__("%Y-%m-%d"))
		return slug

	def set_calculated_fields(self):
		from operator import itemgetter
		photo_difficulty_feedback = list(DifficultyFeedback.objects.filter(photo__id=self.id))
		weighted_level_sum, total_weight = 0, 0
		for each in photo_difficulty_feedback:
			weighted_level_sum += float(each.level) * each.trustworthiness
			total_weight = each.trustworthiness
		if total_weight != 0:
			self.guess_level = round(round(weighted_level_sum, 2) / round(total_weight, 2), 2)

		photo_flip_feedback = list(FlipFeedback.objects.filter(photo__id=self.id))
		flip_feedback_user_dict = {}
		for each in photo_flip_feedback:
			if each.user_profile_id not in flip_feedback_user_dict:
				flip_feedback_user_dict[each.user_profile.id] = [each]
			else:
				flip_feedback_user_dict[each.user_profile.id].append(each)
		votes_for_flipping = 0
		votes_against_flipping = 0
		for user_id, feedback_objects in photo_flip_feedback:
			feedback_objects = sorted(feedback_objects, key=itemgetter("-created"))
			latest_feedback = feedback_objects[0]
			if latest_feedback.flip:
				votes_for_flipping += 1
			else:
				votes_against_flipping += 1
		if votes_for_flipping > votes_against_flipping:
			self.flip = True
		else:
			self.flip = False

		if not self.bounding_circle_radius:
			self.confidence = 0
			self.lon = None
			self.lat = None

			geotags = list(GeoTag.objects.filter(photo__id=self.id, trustworthiness__gt=0.2))
			geotags_with_azimuth = []
			for g in geotags:
				if g.azimuth > 0:
					geotags_with_azimuth.append(g)
			if geotags:
				lon = sorted([g.lon for g in geotags])
				lon = lon[len(lon) / 2]
				lat = sorted([g.lat for g in geotags])
				lat = lat[len(lat) / 2]
				median_azimuth = None
				if len(geotags_with_azimuth) > 0:
					azimuths = sorted([g.azimuth for g in geotags_with_azimuth])
					median_azimuth = azimuths[len(azimuths) / 2]

				correct_guesses_weight, total_weight, azimuth_correct_guesses_weight, azimuth_total_guesses_weight = 0, 0, 0, 0
				lon_sum, lat_sum, azimuth_sum = 0, 0, 0
				user_geotags_map = {}
				for g in geotags:
					current_distance = distance_in_meters(g.lon, g.lat, lon, lat)
					if current_distance < 100:
						if g.user_id not in user_geotags_map:
							user_geotags_map[g.user_id] = g
						else:
							if current_distance < distance_in_meters(user_geotags_map[g.user_id].lon, user_geotags_map[g.user_id].lat, lon, lat):
								user_geotags_map[g.user_id] = g
				for v in user_geotags_map.values():
					correct_guesses_weight += v.trustworthiness
					lon_sum += v.lon * v.trustworthiness
					lat_sum += v.lat * v.trustworthiness
					if v.azimuth > 0 and median_azimuth:
						difference = max(v.azimuth, median_azimuth) - min(v.azimuth, median_azimuth)
						if difference > 180:
							difference = 360 - difference
						if difference <= 15:
							azimuth_sum += v.azimuth * v.trustworthiness
							azimuth_correct_guesses_weight += v.trustworthiness
						azimuth_total_guesses_weight += v.trustworthiness
					total_weight += v.trustworthiness
				unique_correct_guesses_ratio = 0
				if total_weight > 0:
					unique_correct_guesses_ratio = correct_guesses_weight / float(total_weight)
				unique_azimuth_correct_ratio = False
				if azimuth_correct_guesses_weight > 0 and azimuth_total_guesses_weight > 0:
					unique_azimuth_correct_ratio = azimuth_correct_guesses_weight / float(azimuth_total_guesses_weight)

				if unique_correct_guesses_ratio > 0.63:
					self.lon = lon_sum / float(correct_guesses_weight)
					self.lat = lat_sum / float(correct_guesses_weight)
					if unique_azimuth_correct_ratio > 0.63:
						self.azimuth = azimuth_sum / float(azimuth_correct_guesses_weight)
						self.azimuth_confidence = unique_azimuth_correct_ratio * min(1, azimuth_correct_guesses_weight / 3)
					self.confidence = unique_correct_guesses_ratio * min(1, correct_guesses_weight / 3)

class DifficultyFeedback(models.Model):
	photo = models.ForeignKey('Photo')
	user_profile = models.ForeignKey('Profile')
	level = models.PositiveSmallIntegerField(null=False, blank=False)
	trustworthiness = models.FloatField(null=False, blank=False)
	geotag = models.ForeignKey('GeoTag')
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		app_label = "project"

class FlipFeedback(models.Model):
	photo = models.ForeignKey('Photo')
	user_profile = models.ForeignKey('Profile')
	flip = models.NullBooleanField()
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		app_label = "project"

class GeoTag(models.Model):
	MAP, EXIF, GPS = range(3)
	TYPE_CHOICES = (
	(MAP, 'Map'),
	(EXIF, 'EXIF'),
	(GPS, 'GPS'),
	)

	lat = models.FloatField()
	lon = models.FloatField()
	azimuth = models.FloatField(null=True, blank=True)
	zoom_level = models.IntegerField(null=True, blank=True)
	type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES)

	user = models.ForeignKey('Profile', related_name='geotags')
	photo = models.ForeignKey('Photo', related_name='geotags')

	is_correct = models.NullBooleanField()
	score = models.PositiveSmallIntegerField()
	azimuth_score = models.PositiveSmallIntegerField(null=True, blank=True)
	trustworthiness = models.FloatField()

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	class Meta:
		app_label = "project"


class FacebookManager(models.Manager):
	def url_read(self, uri):
		with closing(urlopen(uri)) as request:
			return request.read()

	def get_user(self, access_token, application_id=None):
		data = json_decode(self.url_read("https://graph.facebook.com/me?access_token=%s" % access_token))
		if not data:
			raise "Facebook did not return anything useful for this access token"

		try:
			return self.get(fb_id=data.get('id')), data
		except ObjectDoesNotExist:
			return None, data,

from south.modelsinspector import add_introspection_rules
from oauth2client.django_orm import CredentialsField
add_introspection_rules([], ["^oauth2client\.django_orm\.CredentialsField", "^oauth2client\.django_orm\.FlowField"])


class CredentialsModel(models.Model):
	id = models.ForeignKey(BaseUser, primary_key=True)
	credential = CredentialsField()

	class Meta:
		app_label = "project"


class FlowModel(models.Model):
	id = models.ForeignKey(BaseUser, primary_key=True)
	flow = FlowField()

	class Meta:
		app_label = "project"


class Profile(models.Model):
	facebook = FacebookManager()
	objects = models.Manager()

	user = models.OneToOneField(BaseUser, primary_key=True)

	fb_name = models.CharField(max_length=255, null=True, blank=True)
	fb_link = models.CharField(max_length=255, null=True, blank=True)
	fb_id = models.CharField(max_length=100, null=True, blank=True)
	fb_token = models.CharField(max_length=511, null=True, blank=True)

	google_plus_id = models.CharField(max_length=100, null=True, blank=True)
	google_plus_link = models.CharField(max_length=255, null=True, blank=True)
	google_plus_name = models.CharField(max_length=255, null=True, blank=True)
	google_plus_token = models.CharField(max_length=255, null=True, blank=True)
	google_plus_picture = models.CharField(max_length=255, null=True, blank=True)

	avatar_url = models.URLField(null=True, blank=True)

	modified = models.DateTimeField(auto_now=True)

	score = models.PositiveIntegerField(default=0)
	score_rephoto = models.PositiveIntegerField(default=0)

	@property
	def id(self):
		return self.user_id

	def update_rephoto_score(self):
		rephotos = Photo.objects.filter(rephoto_of__isnull=False, user=self.user)
		total = rephotos.count()
		if total == 0:
			return False

		# every photo gives 2 points
		total *= 2
		distinct = rephotos.values('rephoto_of').order_by().annotate(rephoto_count=Count("user"))
		for p in distinct:
			# every last upload per photo gives 3 extra points
			sp = Photo.objects.filter(rephoto_of=p['rephoto_of']).values('user').order_by('-id')[:1].get()
			if sp and sp['user'] == self.user.id:
				total += 3

		self.score_rephoto = total
		self.save()
		return True

	def update_from_fb_data(self, token, data):
		self.user.first_name = data.get("first_name")
		self.user.last_name = data.get("last_name")
		self.user.save()

		self.fb_token = token
		self.fb_id = data.get("id")
		self.fb_name = data.get("name")
		self.fb_link = data.get("link")
		self.save()

	def update_from_google_plus_data(self, token, data):
		self.user.first_name = data["given_name"]
		self.user.last_name = data["family_name"]
		self.user.save()

		self.google_plus_token = token
		self.google_plus_id = data["id"]
		self.google_plus_link = data["link"]
		self.google_plus_name = data["name"]
		self.google_plus_picture = data["picture"]
		self.save()

	def merge_from_other(self, other):
		other.photos.update(user=self)
		other.skips.update(user=self)
		other.geotags.update(user=self)

	def set_calculated_fields(self):
		self.score = self.geotags.aggregate(
			total_score=models.Sum('score'))['total_score'] or 0

	def __unicode__(self):
		return u'%d - %s - %s' % (self.user.id, self.user.username, self.user.get_full_name())

	class Meta:
		app_label = "project"


class Source(models.Model):
	name = models.CharField(max_length=255)
	description = models.TextField(null=True, blank=True)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return self.name

	class Meta:
		app_label = "project"


class Device(models.Model):
	camera_make = models.CharField(null=True, blank=True, max_length=255)
	camera_model = models.CharField(null=True, blank=True, max_length=255)
	lens_make = models.CharField(null=True, blank=True, max_length=255)
	lens_model = models.CharField(null=True, blank=True, max_length=255)
	software = models.CharField(null=True, blank=True, max_length=255)

	class Meta:
		app_label = "project"

	def __unicode__(self):
		return "%s %s %s %s %s" % (self.camera_make, self.camera_model, self.lens_make, self.lens_model, self.software)


class Skip(models.Model):
	class Meta:
		verbose_name = 'Skip'
		verbose_name_plural = 'Skips'
		app_label = "project"

	user = models.ForeignKey(Profile, related_name='skips')
	photo = models.ForeignKey(Photo)

	created = models.DateTimeField(auto_now_add=True)


class Action(models.Model):
	type = models.CharField(max_length=255)

	related_type = models.ForeignKey(ContentType, null=True, blank=True)
	related_id = models.PositiveIntegerField(null=True, blank=True)
	related_object = generic.GenericForeignKey('related_type', 'related_id')

	params = json.JSONField(null=True, blank=True)

	@classmethod
	def log(cls, type, params=None, related_object=None, request=None):
		obj = cls(type=type, params=params)
		if related_object:
			obj.related_object = related_object
		obj.save()
		return obj

	class Meta:
		app_label = "project"