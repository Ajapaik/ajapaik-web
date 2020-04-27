import os
from contextlib import closing
from copy import deepcopy
from datetime import datetime
from io import StringIO
from json import loads
from math import degrees
from time import sleep
from urllib.request import urlopen

import numpy
from PIL import Image
from bulk_update.manager import BulkUpdateManager
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db.models import Model, TextField, FloatField, CharField, BooleanField, BigIntegerField, \
    ForeignKey, IntegerField, DateTimeField, ImageField, URLField, ManyToManyField, SlugField, \
    PositiveSmallIntegerField, PointField, Manager, NullBooleanField, PositiveIntegerField
from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.urls import reverse
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db.models import CASCADE, DateField, FileField, Lookup, OneToOneField, Q
from django.db.models.fields import Field
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.translation import ugettext as _
from django_comments_xtd.models import XtdComment, LIKEDIT_FLAG, DISLIKEDIT_FLAG
from django_extensions.db.fields import json
from geopy.distance import great_circle
from haystack import connections
from pandas import DataFrame, Series
from requests import get
from sklearn.cluster import DBSCAN
from sorl.thumbnail import get_thumbnail, delete

from ajapaik.ajapaik.phash import phash
from ajapaik.utils import angle_diff
from ajapaik.utils import average_angle


# For filtering empty user first and last name, actually, can be done with ~Q, but this is prettier?
class NotEqual(Lookup):
    lookup_name = 'ne'

    def __init__(self, lhs, rhs):
        super(NotEqual, self).__init__(lhs, rhs)

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return '%s <> %s' % (lhs, rhs), params


Field.register_lookup(NotEqual)


def _calc_trustworthiness(user_id):
    user_unique_latest_geotags = GeoTag.objects.filter(user=user_id, origin=GeoTag.GAME).distinct('photo_id') \
        .order_by('photo_id', '-created')
    total_tries = user_unique_latest_geotags.count()
    correct_tries = user_unique_latest_geotags.filter(is_correct=True).count()

    if not correct_tries:
        return 0.00

    trust = float(1 - 0.9 ** float(correct_tries)) * float(correct_tries) / float(total_tries)
    trust = max(trust, 0.01)

    return trust


def _make_fullscreen(photo):
    return {
        'url': reverse('image_full', args=(photo.pk, photo.get_pseudo_slug())),
        'size': [photo.width, photo.height]
    }


def _get_pseudo_slug_for_photo(description, source_key, id):
    if description is not None and description != '':
        slug = '-'.join(slugify(description).split('-')[:6])[:60]
    elif source_key is not None and source_key != '':
        slug = slugify(source_key)
    else:
        slug = slugify(id)

    return slug

# TODO: Somehow this fires from Sift too...also, it fires at least 3 times on user registration, wasteful
def _user_post_save(sender, instance, **kwargs):
    profile = Profile.objects.get_or_create(user=instance)
    if profile and profile[0].user.first_name and profile[0].user.last_name:
        profile[0].first_name = profile[0].user.first_name
        profile[0].last_name = profile[0].user.last_name
        profile[0].save()


post_save.connect(_user_post_save, sender=User)


# Pretty much unused
class Area(Model):
    name = CharField(max_length=255)
    lat = FloatField(null=True)
    lon = FloatField(null=True)

    class Meta:
        db_table = 'project_area'
        app_label = 'ajapaik'

    def __unicode__(self):
        return u'%s' % self.name


class AlbumPhoto(Model):
    CURATED, RECURATED, MANUAL, STILL, UPLOADED, FACE_TAGGED, COLLECTION = range(7)
    TYPE_CHOICES = (
        (CURATED, 'Curated'),
        (RECURATED, 'Re-curated'),
        (MANUAL, 'Manual'),
        (STILL, 'Still'),
        (UPLOADED, 'Uploaded'),
        (FACE_TAGGED, 'Face tagged'),
        (COLLECTION, 'Collection')
    )

    album = ForeignKey('Album', on_delete=CASCADE)
    photo = ForeignKey('Photo', on_delete=CASCADE)
    profile = ForeignKey('Profile', blank=True, null=True, related_name='album_photo_links', on_delete=CASCADE)
    type = PositiveSmallIntegerField(choices=TYPE_CHOICES, default=MANUAL, db_index=True)
    created = DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'project_albumphoto'
        # FIXME: May be causing bugs elsewhere
        # ordering = ['-created']

    def __unicode__(self):
        if self.profile:
            profilename = self.profile.get_display_name()
        else:
            profilename = 'None'

        return u'%d - %d - %s - %s' % (self.album.id, self.photo.id, self.TYPE_CHOICES[self.type][1], profilename)

    def __str__(self):
        return self.__unicode__()

    def delete(self, *args, **kwargs):
        if self.album.atype == Album.CURATED:
            self.photo.area = None
            self.photo.light_save()

        super(AlbumPhoto, self).delete()


class Album(Model):
    CURATED, FAVORITES, AUTO, PERSON, COLLECTION = range(5)
    TYPE_CHOICES = (
        (CURATED, 'Curated'),
        (FAVORITES, 'Favorites'),
        (AUTO, 'Auto'),
        (PERSON, 'Person'),
        (COLLECTION, 'Collection')
    )

    FEMALE, MALE = range(2)
    GENDER_CHOICES = (
        (MALE, _('Male')),
        (FEMALE, _('Female'))
    )

    name = CharField(_('Name'), max_length=255, db_index=True)
    slug = SlugField(null=True, blank=True, max_length=255)
    description = TextField(_('Description'), null=True, blank=True, max_length=2047)
    subalbum_of = ForeignKey('self', blank=True, null=True, related_name='subalbums', on_delete=CASCADE)
    atype = PositiveSmallIntegerField(choices=TYPE_CHOICES)
    profile = ForeignKey('Profile', related_name='albums', blank=True, null=True, on_delete=CASCADE)
    is_public = BooleanField(_('Is public'), default=True)
    open = BooleanField(_('Is open'), default=False)
    ordered = BooleanField(default=False)
    photos = ManyToManyField('Photo', through='AlbumPhoto', related_name='albums')
    videos = ManyToManyField('Video', related_name='albums', blank=True)
    # Why do albums have coordinates anyway?
    lat = FloatField(null=True, blank=True, db_index=True)
    lon = FloatField(null=True, blank=True, db_index=True)
    geography = PointField(srid=4326, null=True, blank=True, geography=True, spatial_index=True)
    cover_photo = ForeignKey('Photo', null=True, blank=True, on_delete=CASCADE)
    cover_photo_flipped = BooleanField(default=False)
    photo_count_with_subalbums = IntegerField(default=0)
    rephoto_count_with_subalbums = IntegerField(default=0)
    geotagged_photo_count_with_subalbums = IntegerField(default=0)
    comments_count_with_subalbums = IntegerField(default=0)
    is_film_still_album = BooleanField(default=False)
    date_of_birth = DateField(blank=True, null=True)
    gender = PositiveSmallIntegerField(choices=GENDER_CHOICES, blank=True, null=True)
    is_public_figure = BooleanField(default=False)
    wikidata_qid = CharField(_('Wikidata identifier'), max_length=255, blank=True, null=True)
    face_encodings = TextField(blank=True, null=True)
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)
    similar_photo_count_with_subalbums = IntegerField(default=0)
    confirmed_similar_photo_count_with_subalbums = IntegerField(default=0)
    source = ForeignKey('Source', null=True, blank=True, on_delete=CASCADE)

    original_lat = None
    original_lon = None

    as_json = None

    class Meta:
        db_table = 'project_album'

    def __unicode__(self):
        if self.as_json:
            return json.dumps({
                'name': self.name,
                'gender': self.gender
            })

        if self.atype == Album.PERSON and self.date_of_birth:
            return u'%s (%s %s)' % (self.name, _('b.'), self.date_of_birth)

        return u'%s' % self.name

    def __str__(self):
        return self.__unicode__()

    def __init__(self, *args, **kwargs):
        super(Album, self).__init__(*args, **kwargs)
        self.original_lat = self.lat
        self.original_lon = self.lon

    def save(self, *args, **kwargs):
        super(Album, self).save(*args, **kwargs)
        self.set_calculated_fields()
        if not self.cover_photo and self.photo_count_with_subalbums > 0:
            random_photo = self.photos.order_by('?').first()
            self.cover_photo = random_photo
            if random_photo and random_photo.flip:
                self.cover_photo_flipped = random_photo.flip
        if not self.lat and not self.lon:
            random_photo_with_location = self.get_geotagged_historic_photo_queryset_with_subalbums().first()
            if random_photo_with_location:
                self.lat = random_photo_with_location.lat
                self.lon = random_photo_with_location.lon
        if self.lat and self.lon and self.lat != self.original_lat and self.lon != self.original_lon:
            self.geography = Point(x=float(self.lon), y=float(self.lat), srid=4326)
        self.original_lat = self.lat
        self.original_lon = self.lon
        super(Album, self).save(*args, **kwargs)
        if self.subalbum_of:
            self.subalbum_of.save()
        connections['default'].get_unified_index().get_index(Album).update_object(self)

    def get_historic_photos_queryset_with_subalbums(self):
        qs = self.photos.filter(rephoto_of__isnull=True)
        for sa in self.subalbums.filter(atype__in=[Album.CURATED, Album.PERSON]):
            qs = qs | sa.photos.filter(rephoto_of__isnull=True)
        return qs.distinct('id')

    def get_geotagged_historic_photo_queryset_with_subalbums(self):
        qs = self.photos.filter(rephoto_of__isnull=True, lat__isnull=False, lon__isnull=False)
        for sa in self.subalbums.filter(atype__in=[Album.CURATED, Album.PERSON]):
            qs = qs | sa.photos.filter(rephoto_of__isnull=True, lat__isnull=False, lon__isnull=False)

        return qs.distinct('id')

    def get_rephotos_queryset_with_subalbums(self):
        qs = self.get_all_photos_queryset_with_subalbums().filter(rephoto_of__isnull=False)

        return qs.distinct('pk')

    def get_all_photos_queryset_with_subalbums(self):
        qs = self.photos.all()
        for sa in self.subalbums.filter(atype__in=[Album.CURATED, Album.PERSON]):
            qs = qs | sa.photos.all()

        photo_ids = qs.values_list('pk', flat=True)

        qs = qs | Photo.objects.filter(rephoto_of__isnull=False, rephoto_of_id__in=photo_ids)

        return qs.distinct('pk')

    def get_comment_count_with_subalbums(self):
        qs = self.get_all_photos_queryset_with_subalbums().filter(comment_count__gt=0)
        count = 0
        for each in qs:
            count += each.comment_count

        return count

    def get_confirmed_similar_photo_count_with_subalbums(self):
        qs = self.get_all_photos_queryset_with_subalbums().exclude(similar_photos__isnull=True)
        count = 0
        for each in qs:
            for similarity in each.similar_photos.all():
                temp = ImageSimilarity.objects.filter(Q(from_photo=each.id) & Q(to_photo=similarity.id))
                for item in temp:
                    if item is not None and item.confirmed is True:
                        count += 1
        return count

    def get_similar_photo_count_with_subalbums(self):
        qs = self.get_all_photos_queryset_with_subalbums().exclude(similar_photos__isnull=True)
        count = 0
        for each in qs:
            for similarity in each.similar_photos.all():
                temp = ImageSimilarity.objects.filter(Q(from_photo=each.id) & Q(to_photo=similarity.id))
                for item in temp:
                    count += 1
        return count

    def set_calculated_fields(self):
        self.photo_count_with_subalbums = self.get_historic_photos_queryset_with_subalbums().count()
        self.rephoto_count_with_subalbums = self.get_rephotos_queryset_with_subalbums().count()
        self.geotagged_photo_count_with_subalbums = self.get_geotagged_historic_photo_queryset_with_subalbums().count()
        self.comments_count_with_subalbums = self.get_comment_count_with_subalbums()
        self.similar_photo_count_with_subalbums = self.get_similar_photo_count_with_subalbums()
        self.confirmed_similar_photo_count_with_subalbums = self.get_confirmed_similar_photo_count_with_subalbums()

    def light_save(self, *args, **kwargs):
        super(Album, self).save(*args, **kwargs)


class Photo(Model):
    objects = Manager()
    bulk = BulkUpdateManager()

    # Removed sorl ImageField because of https://github.com/mariocesar/sorl-thumbnail/issues/295
    image = ImageField(_('Image'), upload_to='uploads', blank=True, null=True, max_length=255, height_field='height',
                       width_field='width')
    image_unscaled = ImageField(upload_to='uploads', blank=True, null=True, max_length=255)
    image_no_watermark = ImageField(upload_to='uploads', blank=True, null=True, max_length=255)
    height = IntegerField(null=True, blank=True)
    width = IntegerField(null=True, blank=True)
    aspect_ratio = FloatField(null=True, blank=True)
    flip = NullBooleanField()
    invert = NullBooleanField()
    stereo = NullBooleanField()
    # In degrees
    rotated = IntegerField(null=True, blank=True)
    date = DateTimeField(null=True, blank=True)
    date_text = CharField(max_length=255, blank=True, null=True)
    title = CharField(max_length=255, blank=True, null=True)
    description = TextField(_('Description'), null=True, blank=True)
    author = CharField(_('Author'), null=True, blank=True, max_length=255)
    uploader_is_author = BooleanField(default=False)
    licence = ForeignKey('Licence', null=True, blank=True, on_delete=CASCADE)
    # Basically keywords describing medium
    types = CharField(max_length=255, blank=True, null=True)
    keywords = TextField(null=True, blank=True)
    # Legacy field name, actually profile
    user = ForeignKey('Profile', related_name='photos', blank=True, null=True, on_delete=CASCADE)
    # Unused, was set manually for some of the very earliest photos
    level = PositiveSmallIntegerField(default=0)
    guess_level = FloatField(default=3)
    lat = FloatField(null=True, blank=True, validators=[MinValueValidator(-85.05115), MaxValueValidator(85)],
                     db_index=True)
    lon = FloatField(null=True, blank=True, validators=[MinValueValidator(-180), MaxValueValidator(180)],
                     db_index=True)
    geography = PointField(srid=4326, null=True, blank=True, geography=True, spatial_index=True)
    # Should effectively lock the location
    bounding_circle_radius = FloatField(null=True, blank=True)
    address = CharField(max_length=255, blank=True, null=True)
    azimuth = FloatField(null=True, blank=True)
    confidence = FloatField(default=0, null=True, blank=True)
    azimuth_confidence = FloatField(default=0, null=True, blank=True)
    source_key = CharField(max_length=100, null=True, blank=True)
    external_id = CharField(max_length=100, null=True, blank=True)
    external_sub_id = CharField(max_length=100, null=True, blank=True)
    source_url = URLField(null=True, blank=True, max_length=1023)
    source = ForeignKey('Source', null=True, blank=True, on_delete=CASCADE)
    device = ForeignKey('Device', null=True, blank=True, on_delete=CASCADE)
    # Useless
    area = ForeignKey('Area', related_name='areas', null=True, blank=True, on_delete=CASCADE)
    rephoto_of = ForeignKey('self', blank=True, null=True, related_name='rephotos', on_delete=CASCADE)
    first_rephoto = DateTimeField(null=True, blank=True, db_index=True)
    latest_rephoto = DateTimeField(null=True, blank=True, db_index=True)
    fb_object_id = CharField(max_length=255, null=True, blank=True)
    comment_count = IntegerField(default=0, null=True, blank=True, db_index=True)
    first_comment = DateTimeField(null=True, blank=True, db_index=True)
    latest_comment = DateTimeField(null=True, blank=True, db_index=True)
    view_count = PositiveIntegerField(default=0)
    first_view = DateTimeField(null=True, blank=True)
    latest_view = DateTimeField(null=True, blank=True)
    like_count = IntegerField(default=0, db_index=True)
    first_like = DateTimeField(null=True, blank=True, db_index=True)
    latest_like = DateTimeField(null=True, blank=True, db_index=True)
    geotag_count = IntegerField(default=0, db_index=True)
    first_geotag = DateTimeField(null=True, blank=True, db_index=True)
    latest_geotag = DateTimeField(null=True, blank=True, db_index=True)
    dating_count = IntegerField(default=0, db_index=True)
    first_dating = DateTimeField(null=True, blank=True, db_index=True)
    latest_dating = DateTimeField(null=True, blank=True, db_index=True)
    created = DateTimeField(auto_now_add=True, db_index=True)
    modified = DateTimeField(auto_now=True)
    gps_accuracy = FloatField(null=True, blank=True)
    gps_fix_age = FloatField(null=True, blank=True)
    # Old picture's zoom level (float [0.5, 4.0])
    cam_scale_factor = FloatField(null=True, blank=True, validators=[MinValueValidator(0.5), MaxValueValidator(4.0)])
    # yaw, pitch, roll: phone orientation (float radians)
    cam_yaw = FloatField(null=True, blank=True)
    cam_pitch = FloatField(null=True, blank=True)
    cam_roll = FloatField(null=True, blank=True)
    video = ForeignKey('Video', null=True, blank=True, related_name='stills', on_delete=CASCADE)
    video_timestamp = IntegerField(null=True, blank=True)
    face_detection_attempted_at = DateTimeField(null=True, blank=True, db_index=True)
    perceptual_hash = BigIntegerField(null=True, blank=True)
    hasSimilar = BooleanField(default=False)
    similar_photos = ManyToManyField('self', through='ImageSimilarity',symmetrical=False)
    postcard_back_of = ForeignKey('self', blank=True, null=True, related_name='postcard_back', on_delete=CASCADE)
    postcard_front_of = ForeignKey('self', blank=True, null=True, related_name='postcard_front', on_delete=CASCADE)

    original_lat = None
    original_lon = None

    class Meta:
        ordering = ['-id']
        db_table = 'project_photo'

    @property
    def people(self):
        people_albums = []
        rectangles = apps.get_model('ajapaik_face_recognition.FaceRecognitionRectangle').objects \
            .filter(photo=self, deleted__isnull=True) \
            .filter(Q(subject_consensus__isnull=False) | Q(subject_ai_guess__isnull=False)).all()
        for rectangle in rectangles:
            if rectangle.subject_consensus:
                people_albums.append(rectangle.subject_consensus)
            elif rectangle.subject_ai_guess:
                people_albums.append(rectangle.subject_ai_guess)

        return set(people_albums)

    @staticmethod
    def get_game_json_format_photo(photo):
        if photo is None:
            return {}
        # TODO: proper JSON serialization
        image = get_thumbnail(photo.image, '1024x1024', upscale=False)
        source_str = ''
        if photo.source:
            source_str = photo.source.description
        ret = {
            'id': photo.id,
            'description': photo.description,
            'sourceKey': photo.source_key,
            'sourceURL': photo.source_url,
            'sourceName': source_str,
            'lat': photo.lat,
            'lon': photo.lon,
            'azimuth': photo.azimuth,
            'big': {
                'url': reverse('image_thumb', args=(photo.pk, 800)),
                'size': [image.width, image.height]
            },
            'flip': photo.flip,
            'large': _make_fullscreen(photo),
            'totalGeotags': photo.geotags.distinct('user').count(),
            'geotagsWithAzimuth': photo.geotags.filter(azimuth__isnull=False).distinct('user').count(),
            'userAlreadyConfirmed': photo.user_already_confirmed,
            'userAlreadyGeotagged': photo.user_already_geotagged,
            'userLikes': photo.user_likes,
            'userLoves': photo.user_loves,
            'userLikeCount': photo.user_like_count
        }

        return ret

    @staticmethod
    def get_next_photo_to_geotag(qs, request):
        profile = request.get_user().profile
        trustworthiness = _calc_trustworthiness(profile.pk)

        all_photos_set = qs
        photo_ids = frozenset(all_photos_set.values_list('id', flat=True))

        user_geotags_for_set = GeoTag.objects.filter(user=profile, photo_id__in=photo_ids)
        user_skips_for_set = Skip.objects.filter(user=profile, photo_id__in=photo_ids)

        user_geotagged_photo_ids = list(user_geotags_for_set.distinct('photo_id').values_list('photo_id', flat=True))
        user_skipped_photo_ids = list(user_skips_for_set.distinct('photo_id').values_list('photo_id', flat=True))
        user_has_seen_photo_ids = set(user_geotagged_photo_ids + user_skipped_photo_ids)
        user_skipped_less_geotagged_photo_ids = set(user_skipped_photo_ids) - set(user_geotagged_photo_ids)

        user_seen_all = False
        nothing_more_to_show = False

        if 'user_skip_array' not in request.session:
            request.session['user_skip_array'] = []

        if trustworthiness < 0.25:
            # Novice users should only receive the easiest images to prove themselves
            ret_qs = all_photos_set.exclude(id__in=user_has_seen_photo_ids).order_by('guess_level', '-confidence')
            if ret_qs.count() == 0:
                # If the user has seen all the photos, offer at random
                user_seen_all = True
                ret_qs = all_photos_set.order_by('?')
        else:
            # Let's try to show the more experienced users photos they have not yet seen at all
            ret_qs = all_photos_set.exclude(id__in=user_has_seen_photo_ids).order_by('?')
            if ret_qs.count() == 0:
                # If the user has seen them all, let's try showing her photos she
                # has skipped (but not in this session) or not marked an azimuth on
                user_seen_all = True
                ret_qs = all_photos_set.filter(id__in=user_skipped_less_geotagged_photo_ids) \
                    .exclude(id__in=request.session['user_skip_array']).order_by('?')
                if ret_qs.count() == 0:
                    # This user has skipped them in this session, show her photos that
                    # don't have a correct geotag from her
                    user_incorrect_geotags = user_geotags_for_set.filter(is_correct=False)
                    user_correct_geotags = user_geotags_for_set.filter(is_correct=True)
                    user_incorrectly_geotagged_photo_ids = set(
                        user_incorrect_geotags.distinct('photo_id').values_list('photo_id', flat=True))
                    user_correctly_geotagged_photo_ids = set(
                        user_correct_geotags.distinct('photo_id').values_list('photo_id', flat=True))
                    user_no_correct_geotags_photo_ids = list(
                        user_incorrectly_geotagged_photo_ids - user_correctly_geotagged_photo_ids)
                    ret_qs = all_photos_set.filter(id__in=user_no_correct_geotags_photo_ids).order_by('?')
                    if ret_qs.count() == 0:
                        ret_qs = all_photos_set.order_by('?')
                        nothing_more_to_show = True
        ret = ret_qs.first()
        last_confirm_geotag_by_this_user_for_ret = None
        if ret:
            last_confirm_geotag_by_this_user_for_ret = ret.geotags.filter(user_id=profile.id, type=GeoTag.CONFIRMATION) \
                .order_by('-created').first()
            ret.user_already_confirmed = False
        if last_confirm_geotag_by_this_user_for_ret and (ret.lat == last_confirm_geotag_by_this_user_for_ret.lat
                                                         and ret.lon == last_confirm_geotag_by_this_user_for_ret.lon):
            ret.user_already_confirmed = True
        if ret:
            ret.user_already_geotagged = ret.geotags.filter(user_id=profile.id).exists()
            ret.user_likes = PhotoLike.objects.filter(profile=profile, photo=ret, level=1).exists()
            ret.user_loves = PhotoLike.objects.filter(profile=profile, photo=ret, level=2).exists()
            ret.user_like_count = PhotoLike.objects.filter(photo=ret).distinct('profile').count()
            ret.view_count += 1
            ret.light_save()

        return [Photo.get_game_json_format_photo(ret), user_seen_all, nothing_more_to_show]

    def __unicode__(self):
        return u'%s - %s (%s) (%s)' % (self.id, self.description, self.date_text, self.source_key)

    def __str__(self):
        return self.__unicode__()

    def __init__(self, *args, **kwargs):
        super(Photo, self).__init__(*args, **kwargs)
        self.original_lat = self.lat
        self.original_lon = self.lon
        self.original_flip = self.flip

    def get_detail_url(self):
        # Legacy URL needs to stay this way for now for Facebook
        return reverse('photo', args=(self.pk,))

    def do_flip(self):
        # FIXME: Somehow fails silently?
        photo_path = settings.MEDIA_ROOT + "/" + str(self.image)
        img = Image.open(photo_path)
        flipped_image = img.transpose(Image.FLIP_LEFT_RIGHT)
        flipped_image.save(photo_path)
        self.flip = not self.flip
        # This delete applies to sorl thumbnail
        delete(self.image, delete_file=False)
        self.light_save()
        self.original_flip = self.flip

    def set_aspect_ratio(self):
        if self.height is not None and self.width is not None:
            self.aspect_ratio = self.width / self.height
            self.light_save()

    def calculate_phash(self):
        img = Image.open(settings.MEDIA_ROOT + '/' + str(self.image))
        self.perceptual_hash = phash(img)
        self.light_save()

    def find_similar(self):
        return
        img = Image.open(settings.MEDIA_ROOT + '/' + str(self.image))
        self.perceptual_hash = phash(img)
        query = 'SELECT * FROM project_photo WHERE rephoto_of_id IS NULL AND perceptual_hash <@ (%s, 8) AND NOT id=%s AND aspect_ratio > %s AND aspect_ratio < %s'
        if self.aspect_ratio is None:
            self.aspect_ratio = self.width / self.height
        photos = Photo.objects.raw(query,[str(self.perceptual_hash),self.id, self.aspect_ratio * 0.8, self.aspect_ratio * 1.25])
        for similar in photos:
            ImageSimilarity.add_or_update(self,similar)
            similar.light_save()
        self.light_save()

    def find_similar_for_existing_photo(self):
        return
        if self.rephoto_of_id is not None:
            return
        if self.aspect_ratio is None:
            self.aspect_ratio = self.width / self.height
        if not (self.lat is None and self.lon is None):
            query = 'SELECT * FROM project_photo WHERE perceptual_hash <@ (%s, 8) AND rephoto_of_id IS NULL AND NOT id=%s AND lat < %s AND lon < %s AND lat > %s AND lon > %s AND aspect_ratio > %s AND aspect_ratio < %s'
            photos = Photo.objects.raw(query,[str(self.perceptual_hash),self.id,(self.lat + 0.0001),(self.lon + 0.0001),(self.lat - 0.0001),(self.lon - 0.0001), self.aspect_ratio * 0.8, self.aspect_ratio * 1.25])
        else:
            query = 'SELECT * FROM project_photo WHERE perceptual_hash <@ (%s, 8) AND NOT id=%s AND rephoto_of_id IS NULL AND aspect_ratio > %s AND aspect_ratio < %s'
            photos = Photo.objects.raw(query,[str(self.perceptual_hash),self.id, self.aspect_ratio * 0.8, self.aspect_ratio * 1.25])
        for similar in photos:
            list1 = ImageSimilarity.objects.filter(Q(from_photo=self.id) & Q(to_photo=similar.id))
            list2 = ImageSimilarity.objects.filter(Q(from_photo=similar.id) & Q(to_photo=self.id))
            if list1.count() < 1 or list2.count() < 1:
                ImageSimilarity.add_or_update(self,similar)
            similar.light_save()
        self.light_save()

    def watermark(self):
        # For ETERA
        padding = 20
        img = Image.open(self.image_no_watermark)
        img = img.convert('RGBA')
        mark = Image.open(os.path.join(settings.STATIC_ROOT, 'images/TLUAR_watermark.png'))
        longest_side = max(img.size[0], img.size[1])
        coeff = float(longest_side) / 1600.00
        w = int(mark.size[0] * coeff)
        h = int(mark.size[1] * coeff)
        mark = mark.resize((w, h))
        layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        position = (img.size[0] - mark.size[0] - padding, padding)
        layer.paste(mark, position)
        img = Image.composite(layer, img, layer)
        tempfile_io = StringIO()
        img.save(tempfile_io, format='JPEG')
        image_file = InMemoryUploadedFile(tempfile_io, None, 'watermarked.jpg', 'image/jpeg', tempfile_io.len, None)

        self.image.save('watermarked.jpg', image_file)

    def get_absolute_url(self):
        return reverse('photo', args=(self.id, self.get_pseudo_slug()))

    def get_pseudo_slug(self):
        if self.description is not None and self.description != '':
            slug = '-'.join(slugify(self.description).split('-')[:6])[:60]
        elif self.source_key is not None and self.source_key != '':
            slug = slugify(self.source_key)
        else:
            slug = slugify(self.created.__format__('%Y-%m-%d'))

        return slug

    def get_heatmap_points(self):
        valid_geotags = self.geotags.distinct('user_id').order_by('user_id', '-created')
        data = []
        for each in valid_geotags:
            serialized = [each.lat, each.lon]
            if each.azimuth:
                serialized.append(each.azimuth)
            data.append(serialized)

        return data

    def reverse_geocode_location(self):
        url_template = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=%0.5f,%0.5f&key=' + settings.GOOGLE_API_KEY
        lat = None
        lon = None
        if self.lat and self.lon:
            lat = self.lat
            lon = self.lon
        else:
            for a in self.albums.all():
                if a.lat and a.lon:
                    lat = a.lat
                    lon = a.lon
                    break
        if lat and lon:
            cached_response = GoogleMapsReverseGeocode.objects.filter(lat='{:.5f}'.format(lat),
                                                                      lon='{:.5f}'.format(lon)).first()
            if cached_response:
                response = cached_response.response
            else:
                sleep(0.2)
                response = get(url_template % (lat, lon))
                decoded_response = loads(response.text)
                if decoded_response['status'] == 'OK' or decoded_response['status'] == 'ZERO_RESULTS':
                    GoogleMapsReverseGeocode(
                        lat='{:.5f}'.format(lat),
                        lon='{:.5f}'.format(lon),
                        response=response.text
                    ).save()
                response = decoded_response
            if response['status'] == 'OK':
                most_accurate_result = response['results'][0]
                self.address = most_accurate_result['formatted_address']
            elif response['status'] == 'OVER_QUERY_LIMIT':
                return
    
    def set_postcard(self, opposite):
        self.postcard_front_of = opposite
        self.save()
        opposite.postcard_back_of = self
        opposite.save()

    def save(self, *args, **kwargs):
        super(Photo, self).save(*args, **kwargs)
        if self.lat and self.lon and self.lat != self.original_lat and self.lon != self.original_lon:
            self.geography = Point(x=float(self.lon), y=float(self.lat), srid=4326)
            self.reverse_geocode_location()
        if self.flip is None:
            self.flip = False
        if self.original_flip is None:
            self.original_flip = False
        if self.flip != self.original_flip:
            self.do_flip()
        self.original_lat = self.lat
        self.original_lon = self.lon
        if not self.first_rephoto:
            first_rephoto = self.rephotos.order_by('created').first()
            if first_rephoto:
                self.first_rephoto = first_rephoto.created
        last_rephoto = self.rephotos.order_by('-created').first()
        if last_rephoto:
            self.latest_rephoto = last_rephoto.created
        super(Photo, self).save(*args, **kwargs)
        if not settings.DEBUG:
            connections['default'].get_unified_index().get_index(Photo).update_object(self)
    
    def add_to_source_album(self, *args, **kwargs):
        if self.source_id is not None and self.source_id > 0:
            sourceAlbum = Album.objects.filter(source_id=self.source_id).first()
            if sourceAlbum is None:
                sourceAlbum = Album(
                    name = self.source.name,
                    slug = self.source.name,
                    atype = Album.COLLECTION,
                    cover_photo = self,
                    source = self.source
                )
                sourceAlbum.save()

            AlbumPhoto(
                type=AlbumPhoto.COLLECTION,
                photo=self,
                album=sourceAlbum
            ).save()

            sourceAlbum.save()

    def light_save(self, *args, **kwargs):
        super(Photo, self).save(*args, **kwargs)

    @staticmethod
    def get_centroid(points):
        # FIXME: Really need numpy for this?
        n = points.shape[0]
        sum_lon = numpy.sum(points[:, 1])
        sum_lat = numpy.sum(points[:, 0])

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

    # TODO: Cut down on the science library use
    def set_calculated_fields(self):
        photo_difficulty_feedback = DifficultyFeedback.objects.filter(photo_id=self.id)
        weighed_level_sum, total_weight = 0, 0
        for each in photo_difficulty_feedback:
            weighed_level_sum += float(each.level) * each.trustworthiness
            total_weight += each.trustworthiness
        if total_weight != 0:
            self.guess_level = round((weighed_level_sum / total_weight), 2)

        if not self.bounding_circle_radius:
            geotags = GeoTag.objects.filter(photo_id=self.id)
            unique_user_geotag_ids = geotags.distinct('user_id').order_by('user_id', '-created') \
                .values_list('id', flat=True)
            self.geotag_count = unique_user_geotag_ids.count()
            unique_user_geotags = geotags.filter(pk__in=unique_user_geotag_ids)
            geotag_coord_map = {}
            for g in unique_user_geotags:
                key = str(g.lat)[:5] + str(g.lon)[:5]
                if key in geotag_coord_map:
                    geotag_coord_map[key].append(g)
                else:
                    geotag_coord_map[key] = [g]
            if unique_user_geotags:
                df = DataFrame(data=[[x.lon, x.lat] for x in unique_user_geotags], columns=['lon', 'lat'])
                coordinates = df[["lon", "lat"]].values
                db = DBSCAN(eps=0.0003, min_samples=1).fit(coordinates)
                labels = db.labels_
                num_clusters = len(set(labels)) - (1 if -1 in labels else 0)
                clusters = Series([coordinates[labels == i] for i in range(num_clusters)])
                lon = []
                lat = []
                members = []
                for i, cluster in clusters.items():
                    if len(cluster) < 3:
                        representative_point = (cluster[0][1], cluster[0][0])
                    else:
                        representative_point = self.get_nearest_point(cluster, self.get_centroid(cluster))
                    lat.append(representative_point[0])
                    lon.append(representative_point[1])
                    members.append(cluster)
                rs = DataFrame({'lat': lat, 'lon': lon, 'members': members})
                max_trust = 0
                point = None
                selected_geotags = None
                for a in rs.itertuples():
                    trust_sum = 0
                    current_geotags = []
                    for each in a[3]:
                        # TODO: This :5 slice randomly became necessary after a pip update...probably a deeper flaw here
                        g = geotag_coord_map[str(each[1])[:5] + str(each[0])[:5]]
                        for gg in g:
                            current_geotags.append(gg)
                            trust_sum += gg.trustworthiness
                    if trust_sum >= max_trust:
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
                            avg = average_angle(arr)
                            deg_avg = degrees(avg)
                            diff_arr = [angle_diff(x, deg_avg) for x in arr]
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
                    else:
                        self.azimuth = None
                        self.azimuth_confidence = None

class ImageSimilarity(Model):
    from_photo = ForeignKey(Photo, on_delete=CASCADE, related_name="from_photo")
    to_photo = ForeignKey(Photo, on_delete=CASCADE, related_name="to_photo")
    confirmed = BooleanField()
    DIFFERENT, SIMILAR, DUPLICATE = range(3)
    SIMILARITY_TYPES = (
        (DIFFERENT, _('Different')),
        (SIMILAR, _('Similar')),
        (DUPLICATE, _('Duplicate'))
    )
    similarity_type = PositiveSmallIntegerField(choices=SIMILARITY_TYPES, blank=True, null=True)
    user_last_modified = ForeignKey('Profile', related_name='user_last_modified', null=True, on_delete=CASCADE)
    created = DateTimeField(auto_now_add=True, db_index=True)
    modified = DateTimeField(auto_now=True)
    
    
    def __add_or_update__(self):
        qs = ImageSimilarity.objects.filter(from_photo=self.from_photo, to_photo=self.to_photo)
        points = 0
        iterator = 0
        if qs.count() > 0:
            for item in qs:
                if iterator > 1:
                    item.delete()
                else:
                    guess = ImageSimilarityGuess(image_similarity=item, guesser=self.user_last_modified, similarity_type=self.similarity_type)
                    guesses = ImageSimilarityGuess.objects.filter(image_similarity_id=item.id).order_by('guesser_id', '-created').all().distinct('guesser_id')
                    if guesses.filter(guesser = self.user_last_modified.id).count() < 1:
                        points = 10
                    item.confirmed = self.confirmed
                    if self.similarity_type is not None:
                        firstGuess = 0
                        secondGuess = 1
                        if self.similarity_type == 0:
                            firstGuess = 2
                        if self.similarity_type == 1:
                            secondGuess = 2   
                        if guesses.filter(similarity_type=self.similarity_type).count() >= (guesses.filter(similarity_type=secondGuess).count() -1) \
                            and len (guesses.filter(similarity_type=self.similarity_type)) >= (guesses.filter(similarity_type=firstGuess).count() - 1):
                            guess.guesser = self.user_last_modified
                            item.similarity_type = self.similarity_type
                            if self.similarity_type == 1 or self.similarity_type == 2:
                                item.from_photo.hasSimilar = True
                                item.to_photo.hasSimilar = True
                            elif self.similarity_type == 0:
                                positiveSimilarities = imageSimilarity.objects.filter((Q(from_photo_id=item.from_photo.id) & Q(to_photo_id=item.to_photo.id) & Q(similarity_type > 0)) | (Q(from_photo_id=item.from_photo.id) & Q(to_photo_id=item.to_photo.id) & Q(similarity_type > 0))).all()
                                if len (positiveSimilarities) < 1:
                                    item.from_photo.hasSimilar = False
                                    item.to_photo.hasSimilar = False
                    item.user_last_modified = self.user_last_modified
                    item.save()
                    firstSimilar = ImageSimilarity.objects.filter(from_photo_id=item.from_photo.id).exclude(similarity_type=0).first()
                    secondSimilar = ImageSimilarity.objects.filter(from_photo_id=item.to_photo.id).exclude(similarity_type=0).first()
                    if firstSimilar is not None:
                        item.from_photo.hasSimilar = True
                    else:
                        item.from_photo.hasSimilar = False
                    item.from_photo.save()
                    if secondSimilar is not None:
                        item.to_photo.hasSimilar = True
                    else:
                        item.to_photo.hasSimilar = False
                    item.to_photo.save()
                    guess.save()
                    if points > 0:
                        Points(
                            user=self.user_last_modified,
                            action=Points.CONFIRM_IMAGE_SIMILARITY,
                            points=points,
                            image_similarity_confirmation = guess,
                            created=timezone.now()
                        ).save()
                iterator += 1
        else:
            self.from_photo.save()
            self.to_photo.save()
            self.save()
            if self.user_last_modified is not None:
                guess = ImageSimilarityGuess(image_similarity=self, guesser = self.user_last_modified, similarity_type=self.similarity_type)
                guess.save()
                points = 10
                if points > 0:
                    Points(
                        user=self.user_last_modified,
                        action=Points.CONFIRM_IMAGE_SIMILARITY,
                        points=points,
                        image_similarity_confirmation = guess,
                        created=timezone.now()
                    ).save()
        return points


    def add_or_update(photo_obj,photo_obj2,confirmed=None,similarity_type=None, profile=None):
        guesser = Profile.objects.filter(user_id=profile).first()
        if confirmed is None:
            confirmed = False
        imageSimilarity = ImageSimilarity(None, from_photo = photo_obj, to_photo=photo_obj2, confirmed=confirmed, similarity_type=similarity_type, user_last_modified=guesser)
        imageSimilarity2 = ImageSimilarity(None, from_photo = photo_obj2, to_photo=photo_obj, confirmed=confirmed, similarity_type=similarity_type, user_last_modified=guesser)
        points = imageSimilarity.__add_or_update__()
        points += imageSimilarity2.__add_or_update__()
        return points

class ImageSimilarityGuess(Model):
    image_similarity = ForeignKey(ImageSimilarity, on_delete=CASCADE, related_name="image_similarity")
    guesser = ForeignKey('Profile', on_delete=CASCADE, related_name="image_similarity_guesser")
    DIFFERENT, SIMILAR, DUPLICATE = range(3)
    SIMILARITY_TYPES = (
        (DIFFERENT, _('Different')),
        (SIMILAR, _('Similar')),
        (DUPLICATE, _('Duplicate'))
    )
    similarity_type = PositiveSmallIntegerField(choices=SIMILARITY_TYPES, blank=True, null=True)
    created = DateTimeField(auto_now_add=True, db_index=True)

class PhotoMetadataUpdate(Model):
    photo = ForeignKey('Photo', related_name='metadata_updates', on_delete=CASCADE)
    old_title = CharField(max_length=255, blank=True, null=True)
    new_title = CharField(max_length=255, blank=True, null=True)
    old_description = TextField(null=True, blank=True)
    new_description = TextField(null=True, blank=True)
    old_author = CharField(null=True, blank=True, max_length=255)
    new_author = CharField(null=True, blank=True, max_length=255)
    created = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'project_photometadataupdate'


class PhotoComment(Model):
    photo = ForeignKey('Photo', related_name='comments', on_delete=CASCADE)
    fb_comment_id = CharField(max_length=255, unique=True)
    fb_object_id = CharField(max_length=255)
    fb_comment_parent_id = CharField(max_length=255, blank=True, null=True)
    fb_user_id = CharField(max_length=255)
    text = TextField()
    created = DateTimeField()

    class Meta:
        db_table = 'project_photocomment'

    def __unicode__(self):
        return u'%s' % self.text[:50]


class PhotoLike(Model):
    photo = ForeignKey('Photo', related_name='likes', on_delete=CASCADE)
    profile = ForeignKey('Profile', related_name='likes', on_delete=CASCADE)
    level = PositiveSmallIntegerField(default=1)
    created = DateTimeField(auto_now_add=True)


class DifficultyFeedback(Model):
    photo = ForeignKey('Photo', on_delete=CASCADE)
    user_profile = ForeignKey('Profile', related_name='difficulty_feedbacks', on_delete=CASCADE)
    level = PositiveSmallIntegerField()
    trustworthiness = FloatField()
    geotag = ForeignKey('GeoTag', on_delete=CASCADE)
    created = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'project_difficultyfeedback'


# FIXME: Unused model?
class FlipFeedback(Model):
    photo = ForeignKey('Photo', on_delete=CASCADE)
    user_profile = ForeignKey('Profile', on_delete=CASCADE)
    flip = NullBooleanField()
    created = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'project_flipfeedback'


class Points(Model):
    objects = Manager()
    bulk = BulkUpdateManager()

    GEOTAG, REPHOTO, PHOTO_UPLOAD, PHOTO_CURATION, PHOTO_RECURATION, DATING, DATING_CONFIRMATION, FILM_STILL, ANNOTATION, CONFIRM_SUBJECT, CONFIRM_IMAGE_SIMILARITY, GUESS_SUBJECT_AGE, GUESS_SUBJECT_GENDER, TRANSCRIBE  = range(14)
    ACTION_CHOICES = (
        (GEOTAG, _('Geotag')),
        (REPHOTO, _('Rephoto')),
        (PHOTO_UPLOAD, _('Photo upload')),
        (PHOTO_CURATION, _('Photo curation')),
        (PHOTO_RECURATION, _('Photo re-curation')),
        (DATING, _('Dating')),
        (DATING_CONFIRMATION, _('Dating confirmation')),
        (FILM_STILL, _('Film still')),
        (ANNOTATION, _('Annotation')),
        (CONFIRM_SUBJECT, _('Confirm subject')),
        (CONFIRM_IMAGE_SIMILARITY, _('Confirm Image similarity')),
        (GUESS_SUBJECT_AGE, _('Guess subject age')),
        (GUESS_SUBJECT_GENDER, _('Guess subject age')),
        (TRANSCRIBE, _('Transcribe')),
    )

    user = ForeignKey('Profile', related_name='points', on_delete=CASCADE)
    action = PositiveSmallIntegerField(choices=ACTION_CHOICES, db_index=True)
    photo = ForeignKey('Photo', null=True, blank=True, on_delete=CASCADE)
    album = ForeignKey('Album', null=True, blank=True, on_delete=CASCADE)
    geotag = ForeignKey('GeoTag', null=True, blank=True, on_delete=CASCADE)
    dating = ForeignKey('Dating', null=True, blank=True, on_delete=CASCADE)
    dating_confirmation = ForeignKey('DatingConfirmation', null=True, blank=True, on_delete=CASCADE)
    annotation = ForeignKey('ajapaik_face_recognition.FaceRecognitionRectangle', null=True, blank=True, on_delete=CASCADE)
    face_recognition_rectangle_subject_data_guess = ForeignKey('ajapaik_face_recognition.FaceRecognitionRectangleSubjectDataGuess', null=True, blank=True, on_delete=CASCADE)
    subject_confirmation = ForeignKey('ajapaik_face_recognition.FaceRecognitionUserGuess', null=True, blank=True, on_delete=CASCADE)
    image_similarity_confirmation = ForeignKey('ImageSimilarityGuess', null=True, blank=True, on_delete=CASCADE)
    points = IntegerField(default=0)
    created = DateTimeField(db_index=True)
    transcription = ForeignKey('Transcription', null=True, blank=True, on_delete=CASCADE)

    class Meta:
        db_table = 'project_points'
        verbose_name_plural = 'Points'
        unique_together = (('user', 'geotag'), ('user', 'dating'), ('user', 'dating_confirmation'),('user', 'subject_confirmation'),('user', 'image_similarity_confirmation'))

    def __unicode__(self):
        return u'%d - %s - %d' % (self.user.id, self.ACTION_CHOICES[self.action], self.points)

class Transcription(Model):
    text = CharField(max_length=5000, null=True, blank=True)
    photo = ForeignKey('Photo', related_name='transcriptions', on_delete=CASCADE)
    user = ForeignKey('Profile', related_name='transcriptions', on_delete=CASCADE)
    created = DateTimeField(auto_now_add=True, db_index=True)
    modified = DateTimeField(auto_now=True)

class TranscriptionFeedback(Model):
    created = DateTimeField(auto_now_add=True, db_index=True)
    user = ForeignKey('Profile', related_name='transcription_feedback', on_delete=CASCADE)
    transcription = ForeignKey(Transcription, on_delete=CASCADE, related_name="transcription")

class GeoTag(Model):
    MAP, EXIF, GPS, CONFIRMATION, STREETVIEW, SOURCE_GEOTAG, ANDROIDAPP = range(7)
    # FIXME: EXIF and GPS have never been used
    TYPE_CHOICES = (
        (MAP, _('Map')),
        (EXIF, _('EXIF')),
        (GPS, _('GPS')),
        (CONFIRMATION, _('Confirmation')),
        (STREETVIEW, _('StreetView')),
        (SOURCE_GEOTAG, _('Source geotag')),
        (ANDROIDAPP, _('Android app')),
    )
    # TODO: Different ways of tagging
    # VANTAGE_POINT, OBJECT, APPROXIMATE = range(3)
    # GEOTAGGER_TYPE_CHOICES = (
    #     (VANTAGE_POINT, _('Vantage point')),
    #     (OBJECT, _('Object')),
    #     (APPROXIMATE, _('Approximate')),
    # )
    GAME, MAP_VIEW, GALLERY, PERMALINK, SOURCE, REPHOTO = range(6)
    ORIGIN_CHOICES = (
        (GAME, _('Game')),
        (MAP_VIEW, _('Map view')),
        (GALLERY, _('Gallery')),
        (PERMALINK, _('Permalink')),
        (SOURCE, _('Source')),
        (REPHOTO, _('Rephoto')),
    )
    GOOGLE_MAP, GOOGLE_SATELLITE, OPEN_STREETMAP, JUKS, NO_MAP = range(5)
    MAP_TYPE_CHOICES = (
        (GOOGLE_MAP, _('Google map')),
        (GOOGLE_SATELLITE, _('Google satellite')),
        (OPEN_STREETMAP, _('OpenStreetMap')),
        (JUKS, _('Juks')),
        (NO_MAP, _('No map')),
    )

    lat = FloatField(validators=[MinValueValidator(-85.05115), MaxValueValidator(85)])
    lon = FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)])
    geography = PointField(srid=4326, null=True, blank=True, geography=True, spatial_index=True)
    azimuth = FloatField(null=True, blank=True)
    azimuth_line_end_lat = FloatField(null=True, blank=True)
    azimuth_line_end_lon = FloatField(null=True, blank=True)
    zoom_level = IntegerField(null=True, blank=True)
    origin = PositiveSmallIntegerField(choices=ORIGIN_CHOICES, default=0)
    type = PositiveSmallIntegerField(choices=TYPE_CHOICES, default=0)
    # geotagger_type = PositiveSmallIntegerField(choices=GEOTAGGER_TYPE_CHOICES, default=0)
    map_type = PositiveSmallIntegerField(choices=MAP_TYPE_CHOICES, default=0)
    hint_used = BooleanField(default=False)
    photo_flipped = BooleanField(default=False)
    user = ForeignKey('Profile', related_name='geotags', null=True, blank=True, on_delete=CASCADE)
    photo = ForeignKey('Photo', related_name='geotags', on_delete=CASCADE)
    is_correct = BooleanField(default=False)
    azimuth_correct = BooleanField(default=False)
    score = IntegerField(null=True, blank=True)
    azimuth_score = IntegerField(null=True, blank=True)
    trustworthiness = FloatField()
    created = DateTimeField(auto_now_add=True, db_index=True)
    modified = DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_geotag'

    def save(self, *args, **kwargs):
        self.geography = Point(x=float(self.lon), y=float(self.lat), srid=4326)

        super(GeoTag, self).save(*args, **kwargs)

    def __unicode__(self):
        # Django admin may crash with too long names
        title = None
        desc = None
        if self.photo.title:
            title = self.photo.title[:50]
        elif self.photo.description:
            desc = self.photo.description[:50]
        if self.user:
            return u'%s - %s - %d' % (title, desc, self.user.id)
        else:
            return u'%s - %s' % (title, desc)


class FacebookManager(Manager):
    @staticmethod
    def url_read(uri):
        with closing(urlopen(uri)) as request:
            return request.read()

    def get_user(self, access_token):
        data = loads(self.url_read('https://graph.facebook.com/v2.5/me?access_token=%s' % access_token))
        if not data:
            raise Exception('Facebook did not return anything useful for this access token')

        try:
            return self.get(fb_id=data.get('id')), data
        except ObjectDoesNotExist:
            return None, data,


class Profile(Model):
    objects = BulkUpdateManager()
    facebook = FacebookManager()

    user = OneToOneField(User, primary_key=True, on_delete=CASCADE)

    first_name = CharField(max_length=255, null=True, blank=True)
    last_name = CharField(max_length=255, null=True, blank=True)

    fb_name = CharField(max_length=255, null=True, blank=True)
    fb_link = CharField(max_length=255, null=True, blank=True)
    fb_id = CharField(max_length=100, null=True, blank=True, db_index=True)
    fb_token = CharField(max_length=511, null=True, blank=True)
    fb_hometown = CharField(max_length=511, null=True, blank=True)
    fb_current_location = CharField(max_length=511, null=True, blank=True)
    fb_birthday = DateField(null=True, blank=True)
    fb_email = CharField(max_length=255, null=True, blank=True, db_index=True)
    fb_user_friends = TextField(null=True, blank=True)

    google_plus_id = CharField(max_length=100, null=True, blank=True, db_index=True)
    google_plus_email = CharField(max_length=255, null=True, blank=True, db_index=True)
    google_plus_link = CharField(max_length=255, null=True, blank=True)
    google_plus_name = CharField(max_length=255, null=True, blank=True)
    google_plus_token = TextField(null=True, blank=True)
    google_plus_picture = CharField(max_length=255, null=True, blank=True)

    modified = DateTimeField(auto_now=True)
    deletion_attempted = DateTimeField(blank=True, null=True, db_index=True)

    score = PositiveIntegerField(default=0, db_index=True)
    score_rephoto = PositiveIntegerField(default=0, db_index=True)
    score_recent_activity = PositiveIntegerField(default=0, db_index=True)

    class Meta:
        db_table = 'project_profile'

    @property
    def id(self):
        return self.user_id

    def is_legit(self):
        if self.user.is_active and (self.user.email or self.user.socialaccount_set.all() ):
            return True

        return False

    def get_display_name(self):
        if self.first_name and self.last_name:
            return '%s %s' % (self.first_name, self.last_name)
        elif self.google_plus_name:
            return self.google_plus_name
        elif self.fb_name:
            return self.fb_name
        elif self.google_plus_email:
            try:
                return self.google_plus_email.split('@')[0]
            except:
                return _('Anonymous user')
        else:
            return _('Anonymous user')

    def __unicode__(self):
        return u"%s" % (self.get_display_name(),)

    def __str__(self):
        return self.__unicode__()

    def merge_from_other(self, other):
        other.photos.update(user=self)
        other.skips.update(user=self)
        other.geotags.update(user=self)
        other.points.update(user=self)
        other.likes.update(profile=self)
        other.datings.update(profile=self)
        other.dating_confirmations.update(profile=self)

    def update_rephoto_score(self):
        photo_ids_rephotographed_by_this_user = Photo.objects.filter(
            rephoto_of__isnull=False, user_id=self.user.id).values_list('rephoto_of', flat=True)
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
                    Points.objects.get(action=Points.REPHOTO, photo=oldest_rephoto)
                except ObjectDoesNotExist:
                    new_record = Points(
                        user=oldest_rephoto.user,
                        action=Points.REPHOTO,
                        photo=oldest_rephoto,
                        points=1250,
                        created=oldest_rephoto.created
                    )
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
                        Points.objects.get(action=Points.REPHOTO, photo=rp)
                    except ObjectDoesNotExist:
                        new_record = Points(
                            user=rp.user,
                            action=Points.REPHOTO,
                            photo=rp,
                            points=current_score,
                            created=rp.created
                        )
                        new_record.save()
                    user_rephoto_score += current_score

        self.score_rephoto = user_rephoto_score
        self.save()

    def set_calculated_fields(self):
        all_time_score = 0
        for p in self.points.all():
            if p.points:
                all_time_score += p.points
        self.score = all_time_score

class Source(Model):
    name = CharField(max_length=255)
    description = TextField(null=True, blank=True)
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'project_source'


class Device(Model):
    camera_make = CharField(null=True, blank=True, max_length=255)
    camera_model = CharField(null=True, blank=True, max_length=255)
    lens_make = CharField(null=True, blank=True, max_length=255)
    lens_model = CharField(null=True, blank=True, max_length=255)
    software = CharField(null=True, blank=True, max_length=255)

    class Meta:
        db_table = 'project_device'

    def __unicode__(self):
        return '%s %s %s %s %s' % (self.camera_make, self.camera_model, self.lens_make, self.lens_model, self.software)


class Skip(Model):
    user = ForeignKey('Profile', related_name='skips', on_delete=CASCADE)
    photo = ForeignKey('Photo', on_delete=CASCADE)
    created = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'project_skip'

    def __unicode__(self):
        return '%i %i' % (self.user.pk, self.photo.pk)


# TODO: Do we need this? Kind of violating users' privacy, no?
class Action(Model):
    type = CharField(max_length=255)
    related_type = ForeignKey(ContentType, null=True, blank=True, on_delete=CASCADE)
    related_id = PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('related_type', 'related_id')
    params = json.JSONField(null=True, blank=True)

    @classmethod
    def log(cls, my_type, params=None, related_object=None, request=None):
        obj = cls(type=my_type, params=params)
        if related_object:
            obj.related_object = related_object
        obj.save()

        return obj

    class Meta:
        db_table = 'project_action'


class CSVPhoto(Photo):
    # This is a fake class for adding an admin page
    class Meta:
        proxy = True

        # Possible fix for proxy models not getting their auto-generated permissions and stuff
        # class Migration(SchemaMigration):
        # 	def forwards(self, orm):
        # 		orm.send_create_signal('ajapaik', ['CSVPhoto'])
        #
        # 	def backwards(self, orm):
        # 		pass


class NorwegianCSVPhoto(Photo):
    class Meta:
        proxy = True


class Licence(Model):
    name = CharField(max_length=255)
    url = URLField(blank=True, null=True)
    image_url = URLField(blank=True, null=True)
    is_public = BooleanField(default=False)

    class Meta:
        db_table = 'project_licence'

    def __unicode__(self):
        return '%s' % self.name

    def __str__(self):
        return self.__unicode__()


class GoogleMapsReverseGeocode(Model):
    lat = FloatField(validators=[MinValueValidator(-85.05115), MaxValueValidator(85)], db_index=True)
    lon = FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)], db_index=True)
    response = json.JSONField()

    class Meta:
        db_table = 'project_googlemapsreversegeocode'

    def __unicode__(self):
        return '%d;%d' % (self.lat, self.lon)


class Dating(Model):
    DAY, MONTH, YEAR = range(3)
    ACCURACY_CHOICES = (
        (DAY, _('Day')),
        (MONTH, _('Month')),
        (YEAR, _('Year')),
    )

    photo = ForeignKey('Photo', related_name='datings', on_delete=CASCADE)
    profile = ForeignKey('Profile', related_name='datings', on_delete=CASCADE)
    raw = CharField(max_length=25, null=True, blank=True)
    comment = TextField(blank=True, null=True)
    start = DateField(default=datetime.strptime('01011000', '%d%m%Y').date())
    start_approximate = BooleanField(default=False)
    start_accuracy = PositiveSmallIntegerField(choices=ACCURACY_CHOICES, blank=True, null=True)
    end = DateField(default=datetime.strptime('01013000', '%d%m%Y').date())
    end_approximate = BooleanField(default=False)
    end_accuracy = PositiveSmallIntegerField(choices=ACCURACY_CHOICES, blank=True, null=True)
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_dating'

    def __unicode__(self):
        return '%s - %s' % (self.profile.pk, self.photo.pk)


class DatingConfirmation(Model):
    confirmation_of = ForeignKey('Dating', related_name='confirmations', on_delete=CASCADE)
    profile = ForeignKey('Profile', related_name='dating_confirmations', on_delete=CASCADE)
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_datingconfirmation'

    def __unicode__(self):
        return '%s - %s' % (self.profile.pk, self.confirmation_of.pk)


class Video(Model):
    name = CharField(max_length=255)
    slug = SlugField(null=True, blank=True, max_length=255, unique=True)
    file = FileField(upload_to='videos', blank=True, null=True)
    width = IntegerField()
    height = IntegerField()
    author = CharField(max_length=255, blank=True, null=True)
    date = DateField(blank=True, null=True)
    source = ForeignKey('Source', blank=True, null=True, on_delete=CASCADE)
    source_key = CharField(max_length=255, blank=True, null=True)
    source_url = URLField(blank=True, null=True)
    cover_image = ImageField(upload_to='videos/covers', height_field='cover_image_height',
                             width_field='cover_image_width', blank=True, null=True)
    cover_image_height = IntegerField(blank=True, null=True)
    cover_image_width = IntegerField(blank=True, null=True)
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_video'

    def save(self, *args, **kwargs):
        super(Video, self).save(*args, **kwargs)
        if not self.slug:
            self.slug = slugify(self.name)
            super(Video, self).save(*args, **kwargs)

    def __unicode__(self):
        return '%s' % (self.name,)

    def get_absolute_url(self):
        return reverse('videoslug', args=(self.id, self.slug))


class MyXtdComment(XtdComment):
    facebook_comment_id = CharField(max_length=255, blank=True, null=True)

    def save(self, **kwargs):
        super(MyXtdComment, self).save(**kwargs)
        photo = Photo.objects.filter(pk=self.object_pk).first()
        if photo:
            if not photo.first_comment:
                photo.first_comment = self.submit_date
            if not photo.latest_comment or photo.latest_comment < self.submit_date:
                photo.latest_comment = self.submit_date
            photo.comment_count = MyXtdComment.objects.filter(
                object_pk=self.object_pk, is_removed=False
            ).count()
            photo.light_save()

    def delete(self, *args, **kwargs):
        object_pk = deepcopy(self.object_pk)
        super(MyXtdComment, self).delete(*args, **kwargs)
        photo = Photo.objects.filter(pk=object_pk).first()
        if photo:
            photo.comment_count = MyXtdComment.objects.filter(
                object_pk=self.object_pk, is_removed=False
            ).count()
            if photo.comment_count == 0:
                photo.first_comment = None
                photo.latest_comment = None
            else:
                first_comment = MyXtdComment.objects.filter(
                    object_pk=self.object_pk, is_removed=False
                ).order_by('-submit_date').first()
                if first_comment:
                    photo.first_comment = first_comment.submit_date
                latest_comment = MyXtdComment.objects.filter(
                    object_pk=self.object_pk, is_removed=False
                ).order_by('submit_date').first()
                if latest_comment:
                    photo.latest_comment = latest_comment.submit_date

            photo.light_save()

    def like_count(self):
        return self.flags.filter(flag=LIKEDIT_FLAG).count()

    def dislike_count(self):
        return self.flags.filter(flag=DISLIKEDIT_FLAG).count()
