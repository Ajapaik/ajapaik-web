from django import forms
from .models import Photo, GeoTag

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