from django.db import models

from django.contrib.auth.models import User as BaseUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

#from filebrowser.fields import FileBrowseField
from django_extensions.db.fields import json

class Photo(models.Model):
    #image = FileBrowseField("Image", directory="images/", extensions=['.jpg','.png'], max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='uploads/', max_length=200, blank=True, null=True)
    
    date = models.DateField(null=True, blank=True)
    date_text = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    
    user = models.ForeignKey('Profile', blank=True, null=True)
    
    level = models.PositiveSmallIntegerField(default=0)
    guess_level = models.FloatField(null=True, blank=True)
    
    source_key = models.CharField(max_length=100, null=True, blank=True)
    source = models.ForeignKey('Source', null=True, blank=True)
    
    rephoto_of = models.ForeignKey('self', blank=True, null=True, related_name='rephotos')
    
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
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
    user_ptr = models.OneToOneField(BaseUser, primary_key=True)
    
    fb_id = models.IntegerField(null=True, blank=True)
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

class Action(models.Model):
    type = models.CharField(max_length=255)
    
    related_type = models.ForeignKey(ContentType)
    related_id = models.PositiveIntegerField()
    related_object = generic.GenericForeignKey('related_type', 'related_id')
    
    params = json.JSONField(null=True, blank=True)
