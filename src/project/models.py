from django.db import models

from django.contrib.auth.models import User as BaseUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

#from filebrowser.fields import FileBrowseField
from django_extensions.db.fields import json
from django.template.defaultfilters import slugify

from sorl.thumbnail import ImageField

import math

# Create profile automatically
def user_post_save(sender, instance, **kwargs):
    profile, new = Profile.objects.get_or_create(user=instance)

models.signals.post_save.connect(user_post_save, sender=BaseUser)

class City(models.Model):
    name = models.TextField()
    lat = models.FloatField()
    lon = models.FloatField()
    
    def __unicode__(self):
        return u'%s' % self.name

class Photo(models.Model):
    #image = FileBrowseField("Image", directory="images/", extensions=['.jpg','.png'], max_length=200, blank=True, null=True)
    image = ImageField(upload_to='uploads/', max_length=200, blank=True, null=True)
    
    #slug = models.SlugField(null=True, blank=True)
    
    date = models.DateField(null=True, blank=True)
    date_text = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    
    user = models.ForeignKey('Profile', related_name='photos', blank=True, null=True)
    
    level = models.PositiveSmallIntegerField(default=0)
    guess_level = models.FloatField(null=True, blank=True)

    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    confidence = models.FloatField(default=0)

    source_key = models.CharField(max_length=100, null=True, blank=True)
    source = models.ForeignKey('Source', null=True, blank=True)
    
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
        if self.description is not None:
            desc = "%s-" % "-".join(slugify(self.description).split('-')[:6])[:60]
        else:
            desc = ""
        if self.source_key is None or not "_" in self.source_key:
            return "%s%s" % (desc, self.source or "AJAPAIK")
        else:
            return "%s%s_%s" % (desc, self.source or "AJAPAIK", self.source_key)
    
    @staticmethod
    def distance_in_meters(lon1,lat1,lon2,lat2):
        lat_coeff = math.cos(math.radians((lat1 + lat2)/2.0))
        return (2*6350e3*3.1415/360) * math.sqrt( \
                                (lat1 - lat2)**2 + \
                                ((lon1 - lon2)*lat_coeff)**2)

    def set_calculated_fields(self):
        self.confidence = 0
        self.lon = None
        self.lat = None

        geotags = list(GeoTag.objects.filter(photo__id=self.id,
									trustworthiness__gt=0.2))
        if geotags:
            lon = sorted([g.lon for g in geotags])
            lon = lon[len(lon)/2]
            lat = sorted([g.lat for g in geotags])
            lat = lat[len(lat)/2]

            correct_guesses_weight, total_weight = 0,0
            lon_sum, lat_sum = 0,0
            for g in geotags:
                if Photo.distance_in_meters(g.lon, g.lat,
											lon, lat) < 100:
                    correct_guesses_weight += g.trustworthiness
                    lon_sum += g.lon * g.trustworthiness
                    lat_sum += g.lat * g.trustworthiness
                total_weight += g.trustworthiness
            correct_guesses_ratio = correct_guesses_weight / \
                                           float(total_weight)
            if correct_guesses_ratio > 0.63:
                self.lon = lon_sum / float(correct_guesses_weight)
                self.lat = lat_sum / float(correct_guesses_weight)
                self.confidence = correct_guesses_ratio * \
                             min(1,correct_guesses_weight / 1.5)

class GeoTag(models.Model):
    MAP, EXIF, GPS = range(3)
    TYPE_CHOICES = (
        (MAP, 'Map'),
        (EXIF, 'EXIF'),
        (GPS, 'GPS'),
    )

    lat = models.FloatField()
    lon = models.FloatField()
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES)
    
    user = models.ForeignKey('Profile', related_name='geotags')
    photo = models.ForeignKey('Photo', related_name='geotags')

    is_correct = models.NullBooleanField()
    score = models.PositiveSmallIntegerField()
    trustworthiness = models.FloatField()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
class Profile(models.Model):
    user = models.OneToOneField(BaseUser, primary_key=True)
    
    fb_name = models.CharField(max_length=255, null=True, blank=True)
    fb_link = models.CharField(max_length=255, null=True, blank=True)
    fb_id = models.CharField(max_length=100, null=True, blank=True)
    fb_token = models.CharField(max_length=255, null=True, blank=True)
    
    avatar_url = models.URLField(null=True, blank=True)
    
    modified = models.DateTimeField(auto_now=True)

    score = models.PositiveIntegerField(default=0)

    def merge_from_other(self, other):
        other.photos.update(user=self)
        other.guesses.update(user=self)
        other.geotags.update(user=self)

    def set_calculated_fields(self):
        self.score=self.geotags.aggregate(
            total_score=models.Sum('score'))['total_score'] or 0

    def __unicode__(self):
        return u'%d - %s - %s' % (self.user.id, self.user.username, self.user.get_full_name())
    
class Source(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.name
    
class Guess(models.Model):
    class Meta:
        verbose_name = 'Guess'
        verbose_name_plural = 'Guesses'
        
    user = models.ForeignKey(Profile, related_name='guesses')
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
