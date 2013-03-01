from django import forms
from .models import Photo, GeoTag, City
from django.db import models

CITY_CHOICES = City.objects.annotate(num_photos=models.Count('cities')).filter(num_photos__gt=0).order_by('id').values_list('pk','name')

class CitySelectForm(forms.Form):
    city = forms.ChoiceField(choices=CITY_CHOICES, label="Vali linn")

class GeoTagAddForm(forms.Form):
    photo_id = forms.CharField()
    lat = forms.CharField()
    lon = forms.CharField()
    
    def save(self, profile_obj):
        photo_obj = Photo.objects.get(id=self.cleaned_data['photo_id'])
        geo, created = GeoTag.objects.get_or_create(user=profile_obj, photo=photo_obj, defaults={
            'lat': self.cleaned_data['lat'],
            'lon': self.cleaned_data['lon'],
            'type': GeoTag.MAP,
            
        })