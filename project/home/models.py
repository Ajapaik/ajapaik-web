from PIL import Image
from django.core.files import File
from django.contrib.gis.db import models
from django.db import connection

from django.contrib.auth.models import User as BaseUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django_extensions.db.fields import json
from django.template.defaultfilters import slugify
from django.db.models import Q
import os

from urllib2 import urlopen
from contextlib import closing
from json import loads as json_decode
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from oauth2client.django_orm import FlowField

from sorl.thumbnail import get_thumbnail
from django.contrib.gis.geos import Point

import math
import datetime

# Create profile automatically
def user_post_save(sender, instance, **kwargs):
    profile, new = Profile.objects.get_or_create(user=instance)


def distance_in_meters(lon1, lat1, lon2, lat2):
    if not lon1 or not lat1 or not lon2 or not lat2:
        return None
    lat_coeff = math.cos(math.radians((lat1 + lat2) / 2.0))
    return (2 * 6350e3 * 3.1415 / 360) * math.sqrt((lat1 - lat2) ** 2 + ((lon1 - lon2) * lat_coeff) ** 2)


#TODO: Are these really needed?
def _make_thumbnail(photo, size):
    image = get_thumbnail(photo.image, size)
    return {'url': image.url, 'size': [image.width, image.height]}


def _make_fullscreen(photo):
    image = get_thumbnail(photo.image, '1024x1024', upscale=False)
    return {'url': image.url, 'size': [image.width, image.height]}

models.signals.post_save.connect(user_post_save, sender=BaseUser)


class Area(models.Model):
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
        (COLLECTION, 'Collection')
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    atype = models.PositiveSmallIntegerField(choices=TYPE_CHOICES)
    profile = models.ForeignKey('Profile', related_name='albums', blank=True, null=True)

    is_public = models.BooleanField(default=True)

    photos = models.ManyToManyField('Photo', through='AlbumPhoto', related_name='albums')

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "project"

    def __unicode__(self):
        return u'%s' % self.name

    def save(self, *args, **kwargs):
        # Update POSTGIS data on save
        try:
            self.geography = Point(float(self.lat), float(self.lon))
        except:
            pass
        super(Album, self).save(*args, **kwargs)


class AlbumPhoto(models.Model):
    album = models.ForeignKey('Album')
    photo = models.ForeignKey('Photo')
    sort_order = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        app_label = "project"


class PhotoManager(models.GeoManager):
    def get_queryset(self):
        return self.model.QuerySet(self.model)


from django.utils.deconstruct import deconstructible
from uuid import uuid4


@deconstructible
class PathAndRename(object):
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(self.path, filename)


path_and_rename = PathAndRename("uploads")


class Photo(models.Model):
    objects = PhotoManager()

    id = models.AutoField(primary_key=True)
    #Removed sorl ImageField because of https://github.com/mariocesar/sorl-thumbnail/issues/295
    #image = models.ImageField(upload_to=path_and_rename, blank=True, null=True)
    image = models.ImageField(upload_to=path_and_rename, blank=True, null=True)
    image_unscaled = models.ImageField(upload_to=path_and_rename, blank=True, null=True)
    flip = models.NullBooleanField()
    date = models.DateTimeField(null=True, blank=True)
    date_text = models.CharField(max_length=100, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(null=True, blank=True, max_length=2047)
    licence = models.CharField(null=True, blank=True, max_length=255)

    user = models.ForeignKey('Profile', related_name='photos', blank=True, null=True)

    level = models.PositiveSmallIntegerField(default=0)
    guess_level = models.FloatField(null=True, blank=True)

    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    geography = models.PointField(srid=4326, null=True, blank=True, geography=True, spatial_index=True)
    bounding_circle_radius = models.FloatField(null=True, blank=True)
    azimuth = models.FloatField(null=True, blank=True)
    confidence = models.FloatField(default=0)
    azimuth_confidence = models.FloatField(default=0)

    source_key = models.CharField(max_length=100, null=True, blank=True)
    source_url = models.URLField(null=True, blank=True, max_length=1023)
    source = models.ForeignKey('Source', null=True, blank=True)
    device = models.ForeignKey('Device', null=True, blank=True)

    area = models.ForeignKey('Area', related_name='areas', null=True, blank=True)
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
        def get_geotagged_photos_list(self, bounding_box=None, with_images=False):
            # TODO: Once we have regions, re-implement caching
            data = []
            qs = self.filter(confidence__gte=0.3, lat__isnull=False, lon__isnull=False, rephoto_of__isnull=True)
            if bounding_box:
                qs = qs.filter(geography__intersects=bounding_box)
            for p in qs:
                im_url = None
                width = None
                height = None
                rephoto_count = len(list(self.filter(rephoto_of=p.id)))
                # if with_images:
                #     im_url = reverse('project.home.views.photo_thumb', args=(p.id,))
                #     try:
                #         im = get_thumbnail(p.image, "150x150", upscale=False)
                #         width = im._size[0]
                #         height = im._size[1]
                #     except IOError:
                #         pass
                #data.append([p.id, im_url, p.lon, p.lat, rephoto_count, p.flip, p.description, p.azimuth, width, height])
                data.append([p.id, None, p.lon, p.lat, rephoto_count, None, None, p.azimuth, None, None])
            return data


        @staticmethod
        def _get_game_json_format_photo(photo, distance_from_last):
            # TODO: proper JSON serialization
            if not distance_from_last:
                distance_from_last = "Unknown"


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
                "distance_from_last": distance_from_last,
                "total_geotags": photo.geotags.count(),
                "geotags_with_azimuth": photo.geotags.filter(azimuth__isnull=False).count(),
            }

        def get_next_photo_to_geotag(self, request):
            user_id = request.get_user().profile.pk
            from get_next_photos_to_geotag import calc_trustworthiness

            user_trustworthiness = calc_trustworthiness(user_id)

            album_photos_set = self.filter(rephoto_of_id=None)
            album_photo_ids = frozenset([p.id for p in album_photos_set])

            user_geotags_in_album = GeoTag.objects.filter(user=user_id, photo_id__in=album_photo_ids)
            user_skips_in_album = Skip.objects.filter(user=user_id, photo_id__in=album_photo_ids)
            user_last_interacted_photo = None
            distance_between_photos = None
            user_last_geotag = None
            user_last_skip = None
            if len(user_geotags_in_album) > 0:
                user_last_geotag = user_geotags_in_album.order_by("-created")[0]
            if len(user_skips_in_album) > 0:
                user_last_skip = user_skips_in_album.order_by("-created")[0]
            if user_last_skip and user_last_geotag and user_last_skip.created > user_last_geotag.created:
                user_last_action = user_last_skip
            else:
                user_last_action = user_last_geotag
            if user_last_action:
                try:
                    user_last_interacted_photo = album_photos_set.filter(id=user_last_action.photo_id, lat__isnull=False, lon__isnull=False)[:1].get()
                except:
                    user_last_interacted_photo = None

            user_geotagged_photo_ids = list(set(user_geotags_in_album.values_list("photo_id", flat=True)))
            # TODO: Tidy up
            user_skipped_photo_ids = set(list(user_skips_in_album.values_list("photo_id", flat=True)))
            user_skipped_less_geotagged_photo_ids = list(user_skipped_photo_ids - set(list(user_geotags_in_album.values_list("photo_id", flat=True))))
            user_skipped_photo_ids = list(user_skipped_photo_ids)
            user_has_seen_photo_ids = set(user_geotagged_photo_ids + user_skipped_less_geotagged_photo_ids)

            user_seen_all = False
            nothing_more_to_show = False

            if "user_skip_array" not in request.session:
                request.session["user_skip_array"] = []

            # TODO: Restore this maybe?
            #cursor = connection.cursor()
            #cursor.execute(
                #"SELECT A.id, COUNT(G.id) AS geotags FROM project_album A INNER JOIN project_geotag G INNER JOIN project_photo P ON G.photo_id = P.id ON P.city_id = C.id GROUP BY C.id;")
            #result = cursor.fetchall()
            #exception_city_ids = [i[0] for i in result if i[1] > 1000]

            if user_trustworthiness < 0.4:
                # Novice users should only receive the easiest images to prove themselves
                ret = album_photos_set.exclude(id__in=user_has_seen_photo_ids).order_by("-guess_level", "-confidence")
                if len(ret) == 0:
                    # If the user has seen all the photos, offer the easiest or at random
                    #user_seen_all = True
                    #if city_photos_set[0].city_id in exception_city_ids:
                        #ret = city_photos_set.order_by("-guess_level", "-confidence")
                    #else:
                    nothing_more_to_show = True
                    ret = album_photos_set.order_by("?")
            else:
                # Let's try to show the more experienced users photos they have not yet seen at all
                ret = album_photos_set.exclude(id__in=user_has_seen_photo_ids)
                if len(ret) == 0:
                    # If the user has seen them all, let's try showing her photos she has skipped (but not in this session) or not marked an azimuth on
                    user_seen_all = True
                    user_geotags_without_azimuth_in_album = user_geotags_in_album.exclude(azimuth__isnull=False)
                    user_geotagged_without_azimuth_photo_ids = list(set(user_geotags_without_azimuth_in_album.values_list("photo_id", flat=True)))
                    ret = album_photos_set.filter(id__in=(user_geotagged_without_azimuth_photo_ids + user_skipped_less_geotagged_photo_ids)).exclude(id__in=request.session["user_skip_array"])
                    if len(ret) == 0:
                        # TODO: This is half-disabled at the moment
                        # This user has geotagged all the city's photos with azimuths, show her photos that have low confidence or don't have a correct geotag from her
                        # Don't do this for very small/fresh sets (<1000 geotags)
                        #if len(city_photos_set) > 0 and city_photos_set[0].city_id and city_photos_set[0].city_id in exception_city_ids:
                        if len(album_photos_set) > 0:
                            user_incorrect_geotags = user_geotags_in_album.filter(is_correct=False)
                            user_correct_geotags = user_geotags_in_album.filter(is_correct=True)
                            user_incorrectly_geotagged_photo_ids = set(user_incorrect_geotags.values_list("photo_id", flat=True))
                            user_correctly_geotagged_photo_ids = set(user_correct_geotags.values_list("photo_id", flat=True))
                            user_no_correct_geotags_photo_ids = list(user_incorrectly_geotagged_photo_ids - user_correctly_geotagged_photo_ids)
                            ret = album_photos_set.filter(Q(confidence__lt=0.3) | Q(id__in=user_no_correct_geotags_photo_ids))
                        if len(ret) == 0:
                            nothing_more_to_show = True
                good_candidates = []
                shitty_candidates = []
                if user_trustworthiness < 0.4:
                    for p in ret:
                        distance_between_photos = None
                        if user_last_interacted_photo:
                            distance_between_photos = distance_in_meters(p.lon, p.lat, user_last_interacted_photo.lon, user_last_interacted_photo.lat)
                        if p.confidence > 0.7 and distance_between_photos and 250 <= distance_between_photos <= 1000:
                            good_candidates.append(p)
                        elif p.confidence > 0.7:
                            shitty_candidates.append(p)
                elif 0.4 <= user_trustworthiness < 0.7:
                    for p in ret:
                        distance_between_photos = None
                        if user_last_interacted_photo:
                            distance_between_photos = distance_in_meters(p.lon, p.lat, user_last_interacted_photo.lon, user_last_interacted_photo.lat)
                        if 0.4 <= p.confidence <= 0.7 and distance_between_photos and 250 <= distance_between_photos <= 1000:
                            good_candidates.append(p)
                        elif 0.4 <= p.confidence <= 0.7:
                            shitty_candidates.append(p)
                else:
                    for p in ret:
                        distance_between_photos = None
                        if user_last_interacted_photo:
                            distance_between_photos = distance_in_meters(p.lon, p.lat, user_last_interacted_photo.lon, user_last_interacted_photo.lat)
                        if p.confidence < 0.4 and distance_between_photos and 250 <= distance_between_photos <= 1000:
                            good_candidates.append(p)
                        elif p.confidence < 0.4:
                            shitty_candidates.append(p)
                if len(good_candidates) > 0:
                    ret = good_candidates
                else:
                    ret = shitty_candidates
            if ret and ret[0].id in user_skipped_photo_ids:
                request.session["user_skip_array"].append(ret[0].id)
                request.session.modified = True
            if len(ret) == 0:
                random_photo = self._get_game_json_format_photo(album_photos_set.order_by("?")[:1].get(), distance_between_photos)
                return [random_photo], True, True
            return [self._get_game_json_format_photo(ret[0], distance_between_photos)], user_seen_all, nothing_more_to_show

        def get_old_photos_for_grid_view(self, start, end):
            data = []
            for p in self.filter(rephoto_of__isnull=True)[start:end]:
                im_url = reverse('project.home.views.photo_thumb', args=(p.id,))
                try:
                    im = get_thumbnail(p.image, '300x300', upscale=False)
                    data.append([p.id, im_url, im.size[0], im.size[1]])
                except (IOError, TypeError):
                    pass
            return data

        def get_old_photo_count_for_grid_view(self):
            return self.filter(rephoto_of__isnull=True).count()


    def flip_horizontal(self):
        image = Image.open(self.image.path)
        exif = image.info['exif']
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
        image.save(self.image.path, File(image), exif=exif)

    def __unicode__(self):
        return u'%s - %s (%s) (%s)' % (self.id, self.description, self.date_text, self.source_key)

    @models.permalink
    def get_detail_url(self):
        return ('project.home.views.photo', [self.id, ])

    @models.permalink
    def get_absolute_url(self):
        pseudo_slug = self.get_pseudo_slug()
        rephoto = self.rephoto_of
        if rephoto:
            pass
        if pseudo_slug != "":
            return ('project.home.views.photoslug', [self.id, pseudo_slug, ])
        else:
            return ('project.home.views.photo', [self.id, ])

    @models.permalink
    def get_heatmap_url(self):
        pseudo_slug = self.get_pseudo_slug();
        if pseudo_slug != "":
            return ('project.home.views.photoslug_heatmap', [self.id, pseudo_slug, ])
        else:
            return ('project.home.views.photo_heatmap', [self.id, ])

    def get_pseudo_slug(self):
        slug = ""
        if self.description is not None and self.description != "":
            slug = "-".join(slugify(self.description).split('-')[:6])[:60]
        elif self.source_key is not None and self.source_key != "":
            slug = slugify(self.source_key)
        else:
            slug = slugify(self.created.__format__("%Y-%m-%d"))
        return slug

    def get_heatmap_points(self):
        valid_geotags = self.geotags.filter(trustworthiness__gt=0.2)
        data = []
        for each in valid_geotags:
            data.append([each.lat, each.lon, each.azimuth])
        return data

    def save(self, *args, **kwargs):
        # Update POSTGIS data on save
        try:
            self.geography = Point(float(self.lat), float(self.lon))
        except:
            pass
        super(Photo, self).save(*args, **kwargs)

    def set_calculated_fields(self):
        photo_difficulty_feedback = list(DifficultyFeedback.objects.filter(photo__id=self.id))
        weighted_level_sum, total_weight = 0, 0
        for each in photo_difficulty_feedback:
            weighted_level_sum += float(each.level) * each.trustworthiness
            total_weight += each.trustworthiness
        if total_weight != 0:
            self.guess_level = round((weighted_level_sum / total_weight), 2)

        # TODO: Currently not needed
        # photo_flip_feedback = list(FlipFeedback.objects.filter(photo__id=self.id))
        # flip_feedback_user_dict = {}
        # for each in photo_flip_feedback:
        # 	if each.user_profile_id not in flip_feedback_user_dict:
        # 		flip_feedback_user_dict[each.user_profile.id] = [each]
        # 	else:
        # 		flip_feedback_user_dict[each.user_profile.id].append(each)
        # votes_for_flipping = 0
        # votes_against_flipping = 0
        # for user_id, feedback_objects in flip_feedback_user_dict.items():
        # 	feedback_objects = sorted(feedback_objects, key=attrgetter("created"), reverse=True)
        # 	latest_feedback = feedback_objects[0]
        # 	if latest_feedback.flip:
        # 		votes_for_flipping += 1
        # 	else:
        # 		votes_against_flipping += 1
        # if votes_for_flipping > votes_against_flipping:
        # 	self.flip = True
        # else:
        # 	self.flip = False


        if not self.bounding_circle_radius:
            # TODO: What was the purpose of this?
            #self.confidence = 0
            #self.lon = None
            #self.lat = None

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
                            if current_distance < distance_in_meters(user_geotags_map[g.user_id].lon,
                                                                     user_geotags_map[g.user_id].lat, lon, lat):
                                user_geotags_map[g.user_id] = g
                    total_weight += g.trustworthiness
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
                        self.azimuth_confidence = unique_azimuth_correct_ratio * min(1, azimuth_correct_guesses_weight / 2)
                    self.confidence = unique_correct_guesses_ratio * min(1, correct_guesses_weight / 2)

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


class UserMapView(models.Model):
    photo = models.ForeignKey('Photo')
    user_profile = models.ForeignKey('Profile')
    confidence = models.FloatField(default=0)
    action = models.CharField(max_length=255, null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "project"


#TODO: Should create ForeignKey fields here so Django knows to cascade deletes etc.
class Points(models.Model):
    GEOTAG, REPHOTO = range(2)
    ACTION_CHOICES = (
        (GEOTAG, 'Geotag'),
        (REPHOTO, 'Rephoto')
    )

    user = models.ForeignKey('Profile', related_name='points')
    action = models.PositiveSmallIntegerField(choices=ACTION_CHOICES)
    action_reference = models.PositiveIntegerField()
    points = models.PositiveSmallIntegerField(null=True, blank=True)
    created = models.DateTimeField(db_index=True)

    class Meta:
        app_label = "project"


class GeoTag(models.Model):
    MAP, EXIF, GPS = range(3)
    TYPE_CHOICES = (
        (MAP, 'Map'),
        (EXIF, 'EXIF'),
        (GPS, 'GPS'),
    )
    GAME, MAP, GRID = range(3)
    ORIGIN_CHOICES = (
        (GAME, 'Game'),
        (MAP, 'Map'),
        (GRID, 'Grid'),
    )

    lat = models.FloatField()
    lon = models.FloatField()
    geography = models.PointField(srid=4326, null=True, blank=True, geography=True, spatial_index=True)
    azimuth = models.FloatField(null=True, blank=True)
    azimuth_line_end_lat = models.FloatField(null=True, blank=True)
    azimuth_line_end_lon = models.FloatField(null=True, blank=True)
    zoom_level = models.IntegerField(null=True, blank=True)
    origin = models.PositiveSmallIntegerField(choices=ORIGIN_CHOICES, default=0)
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, default=0)

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

# TODO: For Google?
#from south.modelsinspector import add_introspection_rules
from oauth2client.django_orm import CredentialsField
#add_introspection_rules([], ["^oauth2client\.django_orm\.CredentialsField", "^oauth2client\.django_orm\.FlowField"])

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
    fb_hometown = models.CharField(max_length=511, null=True, blank=True)
    fb_current_location = models.CharField(max_length=511, null=True, blank=True)
    fb_birthday = models.DateField(null=True, blank=True)
    fb_email = models.CharField(max_length=255, null=True, blank=True)
    fb_user_friends = models.TextField(null=True, blank=True)

    google_plus_id = models.CharField(max_length=100, null=True, blank=True)
    google_plus_link = models.CharField(max_length=255, null=True, blank=True)
    google_plus_name = models.CharField(max_length=255, null=True, blank=True)
    google_plus_token = models.CharField(max_length=255, null=True, blank=True)
    google_plus_picture = models.CharField(max_length=255, null=True, blank=True)

    avatar_url = models.URLField(null=True, blank=True)

    modified = models.DateTimeField(auto_now=True)

    score = models.PositiveIntegerField(default=0)
    score_rephoto = models.PositiveIntegerField(default=0)
    score_recent_activity = models.PositiveIntegerField(default=0)

    class Meta:
        app_label = "project"

    @property
    def id(self):
        return self.user_id

    def update_from_fb_data(self, token, data):
        self.user.first_name = data.get("first_name")
        self.user.last_name = data.get("last_name")
        self.user.save()

        self.fb_token = token
        self.fb_id = data.get("id")
        self.fb_name = data.get("name")
        self.fb_link = data.get("link")
        self.fb_email = data.get("email")
        self.fb_birthday = datetime.datetime.strptime(data.get("birthday"), '%m/%d/%Y')
        location = data.get("location")
        if location is not None and "name" in location:
            self.fb_current_location = location["name"]
        hometown = data.get("hometown")
        if hometown is not None and "name" in hometown:
            self.fb_hometown = data.get("hometown")["name"]
        self.fb_user_friends = data.get("user_friends")

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
        other.points.update(user=self)

    def update_rephoto_score(self):
        photo_ids_rephotographed_by_this_user = Photo.objects.filter(rephoto_of__isnull=False, user=self.user).values_list("rephoto_of", flat=True)
        original_photos = Photo.objects.filter(id__in=set(photo_ids_rephotographed_by_this_user))

        user_rephoto_score = 0

        for p in original_photos:
            oldest_rephoto = None
            rephotos_by_this_user = []
            for rp in p.rephotos.all():
                if rp.user and rp.user.id == self.user.id:
                    rephotos_by_this_user.append(rp)
                if not oldest_rephoto or rp.created < oldest_rephoto.created:
                    oldest_rephoto = rp
            oldest_rephoto_is_from_this_user = oldest_rephoto.user and self.user and oldest_rephoto.user.id == self.user.id
            user_first_bonus_earned = False
            if oldest_rephoto_is_from_this_user:
                user_first_bonus_earned = True
                user_rephoto_score += 1250
                try:
                    existing_record = Points.objects.filter(action=Points.REPHOTO, action_reference=oldest_rephoto.id).get()
                except ObjectDoesNotExist:
                    new_record = Points(user=oldest_rephoto.user, action=Points.REPHOTO, action_reference=oldest_rephoto.id, points=1250, created=oldest_rephoto.created)
                    new_record.save()
            for rp in rephotos_by_this_user:
                current_score = 250
                if rp.id == oldest_rephoto.id:
                    continue
                else:
                    if not user_first_bonus_earned:
                        current_score = 1000
                        user_first_bonus_earned = True
                    # Check that we have a record in the scoring table
                    try:
                        existing_record = Points.objects.filter(action=Points.REPHOTO, action_reference=rp.id).get()
                    except ObjectDoesNotExist:
                        new_record = Points(user=rp.user, action=Points.REPHOTO, action_reference=rp.id, points=current_score, created=rp.created)
                        new_record.save()
                    user_rephoto_score += current_score

        self.score_rephoto = user_rephoto_score
        self.save()

    def set_calculated_fields(self):
        all_time_score = 0
        for g in self.geotags.all():
            all_time_score += g.score
        self.score = all_time_score + self.score_rephoto

    def __unicode__(self):
        return u'%d - %s - %s' % (self.user.id, self.user.username, self.user.get_full_name())


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
    user = models.ForeignKey(Profile, related_name='skips')
    photo = models.ForeignKey(Photo)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Skip'
        verbose_name_plural = 'Skips'
        app_label = "project"


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


class CSVPhoto(Photo):
    # This is a fake class for adding an admin page
    class Meta:
        proxy = True
        app_label = "project"

        #Possible fix for proxy models not getting their auto-generated permissions and stuff
        # class Migration(SchemaMigration):
        # 	def forwards(self, orm):
        # 		orm.send_create_signal("project", ["CSVPhoto"])
        #
        # 	def backwards(self, orm):
        # 		pass