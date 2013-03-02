from django import forms
from .models import Photo, GeoTag, City
from django.db import models
from django.utils.translation import ugettext as _

CITY_CHOICES = City.objects.annotate(num_photos=models.Count('cities')).filter(num_photos__gt=0).order_by('id').values_list('pk','name')

class CitySelectForm(forms.Form):
    city = forms.ChoiceField(choices=CITY_CHOICES)

    def __init__(self, *args, **kwargs):
        super(CitySelectForm, self).__init__(*args, **kwargs)
        self.fields['city'].label = _("Choose city")

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