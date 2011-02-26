from django.db import models

from django.contrib.auth.models import User as BaseUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

#from filebrowser.fields import FileBrowseField
from django_extensions.db.fields import json

from sorl.thumbnail import ImageField

import math

# Create profile automatically
def user_post_save(sender, instance, **kwargs):
    profile, new = Profile.objects.get_or_create(user=instance)

models.signals.post_save.connect(user_post_save, sender=BaseUser)

class Photo(models.Model):
    #image = FileBrowseField("Image", directory="images/", extensions=['.jpg','.png'], max_length=200, blank=True, null=True)
    image = ImageField(upload_to='uploads/', max_length=200, blank=True, null=True)
    
    date = models.DateField(null=True, blank=True)
    date_text = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    
    user = models.ForeignKey('Profile', blank=True, null=True)
    
    level = models.PositiveSmallIntegerField(default=0)
    guess_level = models.FloatField(null=True, blank=True)

    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    confidence = models.FloatField(default=0)

    source_key = models.CharField(max_length=100, null=True, blank=True)
    source = models.ForeignKey('Source', null=True, blank=True)
    
    rephoto_of = models.ForeignKey('self', blank=True, null=True, related_name='rephotos')
    
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

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

        geotags = list(GeoTag.objects.filter(photo__id=self.id))
        if geotags:
            lon = sorted([g.lon for g in geotags])
            lon = lon[len(lon)/2]
            lat = sorted([g.lat for g in geotags])
            lat = lat[len(lat)/2]

            correct_guesses = 0
            lon_sum, lat_sum = 0,0
            for g in geotags:
                if Photo.distance_in_meters(g.lon, g.lat,
											lon, lat) < 100:
                    correct_guesses += 1
                    lon_sum += g.lon
                    lat_sum += g.lat
            if correct_guesses / float(len(geotags)) > 0.63:
                self.lon = lon_sum / float(correct_guesses)
                self.lat = lat_sum / float(correct_guesses)
                self.confidence = (correct_guesses / 3.0) * \
                        correct_guesses / float(len(geotags))

    
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
    
    user = models.ForeignKey('Profile')
    photo = models.ForeignKey('Photo')
    
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
    
class Source(models.Model):
    name = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
class Guess(models.Model):
    class Meta:
        verbose_name = 'Guess'
        verbose_name_plural = 'Guesses'
        
    user = models.ForeignKey(Profile)
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
        
