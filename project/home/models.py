from PIL import Image
from django.core.files import File
from django.contrib.gis.db import models
from django.core.validators import MinValueValidator
from django.core.validators import MaxValueValidator
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
from django.contrib.gis.geos import Point, Polygon

import math
import datetime

import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from geopy.distance import great_circle

from django.utils.deconstruct import deconstructible
from uuid import uuid4
from django.utils.translation import ugettext as _


# Create profile automatically
def user_post_save(sender, instance, **kwargs):
    Profile.objects.get_or_create(user=instance)


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


def _angle_diff(angle1, angle2):
    diff = angle2 - angle1
    if diff < -180:
        diff += 360
    elif diff > 180:
        diff -= 360
    return abs(diff)


def _average_angle(angles):
    x = y = 0
    for e in angles:
        x += math.cos(math.radians(e))
        y += math.sin(math.radians(e))
    return math.atan2(y, x)


models.signals.post_save.connect(user_post_save, sender=BaseUser)

class Area(models.Model):
    name = models.TextField()
    lat = models.FloatField(null=True)
    lon = models.FloatField(null=True)

    class Meta:
        app_label = "project"

    def __unicode__(self):
        return u'%s' % self.name


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


cat_path_and_rename = PathAndRename("cat")


class CatTag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    level = models.SmallIntegerField(blank=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        app_label = "project"

    def __unicode__(self):
        return u'%s' % self.name


class CatTagPhoto(models.Model):
    tag = models.ForeignKey('CatTag')
    album = models.ForeignKey('CatAlbum')
    photo = models.ForeignKey('CatPhoto')
    profile = models.ForeignKey('Profile')
    value = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "project"

    def __unicode__(self):
        return u'%s - %s - %s - %s' % (self.photo, self.tag, self.value, self.profile)


class CatPhoto(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to=cat_path_and_rename, max_length=255)
    author = models.CharField(max_length=255, null=True, blank=True)
    source = models.ForeignKey('Source', null=True, blank=True)
    source_url = models.URLField(null=True, blank=True, max_length=255)
    source_key = models.CharField(max_length=255, blank=True, null=True)
    tags = models.ManyToManyField(CatTag, related_name='photos', through=CatTagPhoto)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "project"

    def __unicode__(self):
        return u'%s' % self.title

    def _get_source_with_key(self):
        if self.source_key:
            return str(self.source.name + self.source_key)
        return self.source.name


class CatAlbum(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    image = models.ImageField(upload_to=cat_path_and_rename, max_length=255)
    photos = models.ManyToManyField(CatPhoto, related_name='album', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "project"

    def __unicode__(self):
        return u'%s' % self.title


class Album(models.Model):
    CURATED, FAVORITES, AUTO = range(3)
    TYPE_CHOICES = (
        (CURATED, 'Curated'),
        (FAVORITES, 'Favorites'),
        (AUTO, 'Auto')
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(null=True, blank=True, max_length=255)
    description = models.TextField(null=True, blank=True, max_length=2047)
    subalbum_of = models.ForeignKey('self', blank=True, null=True, related_name='subalbums')

    atype = models.PositiveSmallIntegerField(choices=TYPE_CHOICES)
    profile = models.ForeignKey('Profile', related_name='albums', blank=True, null=True)

    is_public = models.BooleanField(default=True)
    is_public_mutable = models.BooleanField(default=False)

    photos = models.ManyToManyField('Photo', through='AlbumPhoto', related_name='albums')

    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "project"

    def __unicode__(self):
        return u'%s' % self.name


class AlbumPhoto(models.Model):
    album = models.ForeignKey('Album')
    photo = models.ForeignKey('Photo')
    sort_order = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        app_label = "project"

    def __unicode__(self):
        return u'%d - %d' % (self.album.id, self.photo.id)


def delete_parent(sender, **kwargs):
    try:
        if len(kwargs["instance"].album.photos.all()) == 1:
            kwargs["instance"].album.delete()
    except:
        pass

models.signals.pre_delete.connect(delete_parent, sender=AlbumPhoto)

class PhotoManager(models.GeoManager):
    def get_queryset(self):
        return self.model.QuerySet(self.model)

path_and_rename = PathAndRename("uploads")


class Photo(models.Model):
    objects = PhotoManager()

    id = models.AutoField(primary_key=True)
    # Removed sorl ImageField because of https://github.com/mariocesar/sorl-thumbnail/issues/295
    image = models.ImageField(upload_to=path_and_rename, blank=True, null=True, max_length=255)
    image_unscaled = models.ImageField(upload_to=path_and_rename, blank=True, null=True, max_length=255)
    height = models.IntegerField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    flip = models.NullBooleanField()
    invert = models.NullBooleanField()
    stereo = models.NullBooleanField()
    date = models.DateTimeField(null=True, blank=True)
    date_text = models.CharField(max_length=100, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(null=True, blank=True, max_length=2047)
    author = models.CharField(null=True, blank=True, max_length=255)
    licence = models.ForeignKey('Licence', null=True, blank=True)
    types = models.CharField(max_length=255, blank=True, null=True)

    user = models.ForeignKey('Profile', related_name='photos', blank=True, null=True)

    level = models.PositiveSmallIntegerField(default=0)
    guess_level = models.FloatField(default=3)

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
        @staticmethod
        def get_album_photo_count_and_total_geotag_count(album_id=None, area_id=None):
            if album_id is not None:
                album_photos = Album.objects.get(pk=album_id).photos.all()
                ungeotagged_qs = album_photos.filter(lat__isnull=True, lon__isnull=True, rephoto_of__isnull=True)
                geotagged_qs = album_photos.filter(lat__isnull=False, lon__isnull=False, rephoto_of__isnull=True)
                return ungeotagged_qs.count(), geotagged_qs.count()
            if area_id is not None:
                area_photos = Photo.objects.filter(area_id=area_id)
                ungeotagged_qs = area_photos.filter(lat__isnull=True, lon__isnull=True, rephoto_of__isnull=True)
                geotagged_qs = area_photos.filter(lat__isnull=False, lon__isnull=False, rephoto_of__isnull=True)
                return ungeotagged_qs.count(), geotagged_qs.count()
            return None, None

        def get_geotagged_photos_list(self, bounding_box=None):
            # TODO: Once we have regions, re-implement caching
            data = []
            qs = self.filter(lat__isnull=False, lon__isnull=False, rephoto_of__isnull=True)
            if bounding_box:
                qs = qs.filter(geography__intersects=Polygon.from_bbox(bounding_box))
            for p in qs:
                rephoto_count = len(list(self.filter(rephoto_of=p.id)))
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
                    user_last_interacted_photo = album_photos_set.filter(id=user_last_action.photo_id)[:1].get()
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

            cursor = connection.cursor()
            cursor.execute(
                "SELECT A.id, COUNT(G.id) AS geotags FROM project_area A INNER JOIN project_geotag G INNER JOIN project_photo P ON G.photo_id = P.id ON P.area_id = A.id GROUP BY A.id;")
            result = cursor.fetchall()
            exception_city_ids = [i[0] for i in result if i[1] > 1000]

            if user_trustworthiness < 0.4:
                # Novice users should only receive the easiest images to prove themselves
                ret = album_photos_set.exclude(id__in=user_has_seen_photo_ids).order_by("guess_level", "-confidence").all()
                if len(ret) == 0:
                    # If the user has seen all the photos, offer the easiest or at random
                    user_seen_all = True
                    if album_photos_set[0].area_id in exception_city_ids:
                        ret = album_photos_set.order_by("guess_level", "-confidence")
                    else:
                        nothing_more_to_show = True
                        ret = album_photos_set.order_by("?")
            else:
                # Let's try to show the more experienced users photos they have not yet seen at all
                ret = album_photos_set.exclude(id__in=user_has_seen_photo_ids).all()
                if len(ret) == 0:
                    # If the user has seen them all, let's try showing her photos she has skipped (but not in this session) or not marked an azimuth on
                    user_seen_all = True
                    user_geotags_without_azimuth_in_album = user_geotags_in_album.exclude(azimuth__isnull=False)
                    user_geotagged_without_azimuth_photo_ids = list(set(user_geotags_without_azimuth_in_album.values_list("photo_id", flat=True)))
                    ret = album_photos_set.filter(id__in=(user_geotagged_without_azimuth_photo_ids + user_skipped_less_geotagged_photo_ids)).exclude(id__in=request.session["user_skip_array"])
                    if len(ret) == 0:
                        # This user has geotagged all the city's photos with azimuths, show her photos that have low confidence or don't have a correct geotag from her
                        # Don't do this for very small/fresh sets (<1000 geotags)
                        if len(album_photos_set) > 0 and album_photos_set[0].area_id and album_photos_set[0].area_id in exception_city_ids:
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
            if len(ret) == 0 or (user_last_interacted_photo and user_last_interacted_photo.id == ret[0].id):
                random_photo = self._get_game_json_format_photo(album_photos_set.order_by("?")[:1].get(), distance_between_photos)
                return [random_photo], False, False
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

    # def delete(self, *args, **kwargs):
    #     self.image.delete()
    #     super(Photo, self).delete(*args, **kwargs)

    def __unicode__(self):
        return u'%s - %s (%s) (%s)' % (self.id, self.description, self.date_text, self.source_key)

    @models.permalink
    def get_detail_url(self):
        return 'project.home.views.photo', [self.id, ]

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
        valid_geotags = self.geotags.all()
        data = []
        for each in valid_geotags:
            data.append([each.lat, each.lon, each.azimuth])
        return data

    def save(self, *args, **kwargs):
        # Update POSTGIS data on save
        try:
            self.geography = Point(x=float(self.lat), y=float(self.lon), srid=4326)
        except:
            pass
        # Calculate average coordinates for album
        album_ids = set(AlbumPhoto.objects.filter(photo_id=self.id).values_list('album_id', flat=True))
        albums = Album.objects.filter(id__in=album_ids).all()
        for a in albums:
            photos_with_location = a.photos.filter(lat__isnull=False, lon__isnull=False).all()
            lat = 0
            lon = 0
            count = 0
            for p in photos_with_location:
                lat += p.lat
                lon += p.lon
                count += 1
            if lat > 0 and lon > 0 and count > 0:
                a.lat = lat / count
                a.lon = lon / count
                a.save()
        super(Photo, self).save(*args, **kwargs)

    @staticmethod
    def get_centroid(points):
        n = points.shape[0]
        sum_lon = np.sum(points[:, 1])
        sum_lat = np.sum(points[:, 0])
        return sum_lon / n, sum_lat / n

    @staticmethod
    def get_nearest_point(set_of_points, point_of_reference):
        closest_point = None
        closest_dist = None
        for point in set_of_points:
            point = (point[1], point[0])
            dist = great_circle(point_of_reference, point).meters
            if (closest_dist is None) or (dist < closest_dist):
                closest_point = point
                closest_dist = dist
        return closest_point

    def set_calculated_fields(self):
        photo_difficulty_feedback = list(DifficultyFeedback.objects.filter(photo_id=self.id))
        weighted_level_sum, total_weight = 0, 0
        for each in photo_difficulty_feedback:
            weighted_level_sum += float(each.level) * each.trustworthiness
            total_weight += each.trustworthiness
        if total_weight != 0:
            self.guess_level = round((weighted_level_sum / total_weight), 2)

        if not self.bounding_circle_radius:
            geotags = GeoTag.objects.filter(photo_id=self.id)
            unique_user_geotag_ids = geotags.distinct('user_id').order_by('user_id', '-created').values_list('id', flat=True)
            unique_user_geotags = geotags.filter(pk__in=unique_user_geotag_ids)
            geotag_coord_map = {}
            for g in unique_user_geotags:
                key = str(g.lat) + str(g.lon)
                if key in geotag_coord_map:
                    geotag_coord_map[key].append(g)
                else:
                    geotag_coord_map[key] = [g]
            if unique_user_geotags:
                df = pd.DataFrame(data=[[x.lon, x.lat] for x in unique_user_geotags], columns=['lon', 'lat'])
                coordinates = df.as_matrix(columns=['lon', 'lat'])
                db = DBSCAN(eps=0.0003, min_samples=1).fit(coordinates)
                labels = db.labels_
                num_clusters = len(set(labels)) - (1 if -1 in labels else 0)
                clusters = pd.Series([coordinates[labels == i] for i in range(num_clusters)])
                lon = []
                lat = []
                members = []
                for i, cluster in clusters.iteritems():
                    if len(cluster) < 3:
                        representative_point = (cluster[0][1], cluster[0][0])
                    else:
                        representative_point = self.get_nearest_point(cluster, self.get_centroid(cluster))
                    lat.append(representative_point[0])
                    lon.append(representative_point[1])
                    members.append(cluster)
                rs = pd.DataFrame({'lat': lat, 'lon': lon, 'members': members})
                max_trust = 0
                point = None
                selected_geotags = None
                for a in rs.itertuples():
                    trust_sum = 0
                    current_geotags = []
                    for each in a[3]:
                        g = geotag_coord_map[str(each[1]) + str(each[0])]
                        for gg in g:
                            current_geotags.append(gg)
                            trust_sum += gg.trustworthiness
                    if trust_sum > max_trust:
                        max_trust = trust_sum
                        point = {'lat': a[1], 'lon': a[2]}
                        selected_geotags = current_geotags
                if point:
                    self.lat = point['lat']
                    self.lon = point['lon']
                    self.confidence = float(len(selected_geotags)) / float(len(geotags))
                geotags.update(is_correct=False, azimuth_correct=False)
                if selected_geotags:
                    GeoTag.objects.filter(pk__in=[x.id for x in selected_geotags]).update(is_correct=True)
                    # TODO: Solution for few very different guesses e.g. (0, 90, 180) => 90
                    filter_indices = []
                    contains_outliers = True
                    arr = [x.azimuth for x in selected_geotags if x.azimuth]
                    initial_arr_length = len(arr)
                    deg_avg = None
                    if initial_arr_length > 0:
                        while contains_outliers:
                            avg = _average_angle(arr)
                            deg_avg = math.degrees(avg)
                            diff_arr = [_angle_diff(x, deg_avg) for x in arr]
                            contains_outliers = False
                            for i, e in enumerate(diff_arr):
                                if e > 60:
                                    filter_indices.append(i)
                                    contains_outliers = True
                            arr = [i for j, i in enumerate(arr) if j not in filter_indices]
                    correct_azimuth_geotags = [i for j, i in enumerate(selected_geotags) if j not in filter_indices]
                    GeoTag.objects.filter(pk__in=[x.id for x in correct_azimuth_geotags]).update(azimuth_correct=True)
                    if deg_avg is not None:
                        self.azimuth = deg_avg
                        self.azimuth_confidence = float(len(arr)) / float(initial_arr_length)




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


class Points(models.Model):
    GEOTAG, REPHOTO, PHOTO_UPLOAD, PHOTO_CURATION = range(4)
    ACTION_CHOICES = (
        (GEOTAG, 'Geotag'),
        (REPHOTO, 'Rephoto'),
        (PHOTO_UPLOAD, 'Photo upload'),
        (PHOTO_CURATION, 'Photo curation'),
    )

    user = models.ForeignKey('Profile', related_name='points')
    action = models.PositiveSmallIntegerField(choices=ACTION_CHOICES)
    action_reference = models.PositiveIntegerField(null=True, blank=True)
    photo = models.ForeignKey('Photo', null=True, blank=True)
    geotag = models.ForeignKey('GeoTag', null=True, blank=True)
    points = models.PositiveSmallIntegerField(null=True, blank=True)
    created = models.DateTimeField(db_index=True)

    class Meta:
        app_label = "project"
        verbose_name_plural = "Points"

    def __unicode__(self):
        return u'%d - %s - %d' % (self.user.id, self.action, self.points)


class GeoTag(models.Model):
    MAP, EXIF, GPS = range(3)
    TYPE_CHOICES = (
        (MAP, _('Map')),
        (EXIF, _('EXIF')),
        (GPS, _('GPS')),
    )
    GAME, MAP_VIEW, GRID = range(3)
    ORIGIN_CHOICES = (
        (GAME, _('Game')),
        (MAP_VIEW, _('Map view')),
        (GRID, _('Grid')),
    )
    GOOGLE_MAP, GOOGLE_SATELLITE, OPEN_STREETMAP = range(3)
    MAP_TYPE_CHOICES = (
        (GOOGLE_MAP, _('Google map')),
        (GOOGLE_SATELLITE, _('Google satellite')),
        (OPEN_STREETMAP, _('Open StreetMap'))
    )
    lat = models.FloatField(validators=[MinValueValidator(-85), MaxValueValidator(85)])
    lon = models.FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)])
    geography = models.PointField(srid=4326, null=True, blank=True, geography=True, spatial_index=True)
    azimuth = models.FloatField(null=True, blank=True)
    azimuth_line_end_lat = models.FloatField(null=True, blank=True)
    azimuth_line_end_lon = models.FloatField(null=True, blank=True)
    zoom_level = models.IntegerField(null=True, blank=True)
    origin = models.PositiveSmallIntegerField(choices=ORIGIN_CHOICES, default=0)
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, default=0)
    map_type = models.PositiveSmallIntegerField(choices=MAP_TYPE_CHOICES, default=0)
    hint_used = models.BooleanField(default=False)
    user = models.ForeignKey('Profile', related_name='geotags')
    photo = models.ForeignKey('Photo', related_name='geotags')
    is_correct = models.BooleanField(default=False)
    azimuth_correct = models.BooleanField(default=False)
    score = models.PositiveSmallIntegerField(null=True, blank=True)
    azimuth_score = models.PositiveSmallIntegerField(null=True, blank=True)
    trustworthiness = models.FloatField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'project'

    def save(self, *args, **kwargs):
        self.geography = Point(x=float(self.lat), y=float(self.lon), srid=4326)
        super(GeoTag, self).save(*args, **kwargs)

    def __unicode__(self):
        # Django admin may crash with too long names
        title = None
        desc = None
        if self.photo.title:
            title = self.photo.title[:50]
        if self.photo.description:
            desc = self.photo.description[:50]
        return u'%s - %s - %s' % (title, desc, self.user.fb_name)


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
        try:
            self.fb_birthday = datetime.datetime.strptime(data.get("birthday"), '%m/%d/%Y')
        except TypeError:
            pass
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
                    existing_record = Points.objects.filter(action=Points.REPHOTO, photo=oldest_rephoto).get()
                except ObjectDoesNotExist:
                    new_record = Points(user=oldest_rephoto.user, action=Points.REPHOTO, photo=oldest_rephoto, points=1250, created=oldest_rephoto.created)
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
                        existing_record = Points.objects.filter(action=Points.REPHOTO, photo=rp).get()
                    except ObjectDoesNotExist:
                        new_record = Points(user=rp.user, action=Points.REPHOTO, photo=rp, points=current_score, created=rp.created)
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

class Licence(models.Model):
    name = models.CharField(max_length=255)
    url = models.TextField(blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)

    class Meta:
        app_label = "project"

    def __unicode__(self):
        return "%s" % self.name