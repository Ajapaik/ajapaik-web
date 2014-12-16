from django import forms
from .models import City
from django.utils.translation import ugettext_lazy as _
from project import settings

# TODO: Make forms for everything, there's too much Javascript going on right now
class CitySelectionForm(forms.Form):
    city = forms.ModelChoiceField(queryset=City.objects.all(), label=_('Choose city'),
                                  initial=City.objects.filter(pk=settings.DEFAULT_CITY_ID))

    def __init__(self, *args, **kwargs):
        super(CitySelectionForm, self).__init__(*args, **kwargs)

        # class CitySelectForm(forms.Form):
        # city = forms.ChoiceField(choices=CITY_CHOICES)
        #
        # def __init__(self, *args, **kwargs):
        # super(CitySelectForm, self).__init__(*args, **kwargs)
        #         self.fields['city'].label = _("Choose city")
        #
        # class GeoTagAddForm(forms.Form):
        #     photo_id = forms.CharField()
        #     lat = forms.CharField()
        #     lon = forms.CharField()
        #
        #     def save(self, profile_obj):
        #         photo_obj = Photo.objects.get(id=self.cleaned_data['photo_id'])
        #         geo, created = GeoTag.objects.get_or_create(user=profile_obj, photo=photo_obj, defaults={
        #             'lat': self.cleaned_data['lat'],
        #             'lon': self.cleaned_data['lon'],
        #             'type': GeoTag.MAP,
        #
        #         })