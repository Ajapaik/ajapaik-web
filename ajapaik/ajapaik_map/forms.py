from django import forms
from django.utils.translation import gettext_lazy as _

from ajapaik.ajapaik.forms import BaseFilteringForm
from ajapaik.ajapaik.models import Album


class MapDataRequestForm(BaseFilteringForm):
    album = forms.ModelChoiceField(queryset=Album.objects.all(), label=_('Choose album'), required=False)
    limit_by_album = forms.BooleanField(initial=False, required=False)
    sw_lat = forms.FloatField(min_value=-85.05115, max_value=85, required=False)
    sw_lon = forms.FloatField(min_value=-180, max_value=180, required=False)
    ne_lat = forms.FloatField(min_value=-85.05115, max_value=85, required=False)
    ne_lon = forms.FloatField(min_value=-180, max_value=180, required=False)
    starting = forms.DateField(required=False)
    ending = forms.DateField(required=False)
    count_limit = forms.IntegerField(min_value=1, required=False)
