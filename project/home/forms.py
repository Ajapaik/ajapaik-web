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