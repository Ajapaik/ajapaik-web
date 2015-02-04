from django import forms
from .models import Area
from django.utils.translation import ugettext_lazy as _
from project import settings

# TODO: Make forms for everything, there's too much Javascript going on right now
class AreaSelectionForm(forms.Form):
    area = forms.ModelChoiceField(queryset=Area.objects.all(), label=_('Choose area'), initial=Area.objects.filter(pk=settings.DEFAULT_AREA_ID))

    def __init__(self, *args, **kwargs):
        super(AreaSelectionForm, self).__init__(*args, **kwargs)

class AddAreaForm(forms.Form):
    name = forms.CharField(max_length=255, required=True)
    lat = forms.FloatField(required=True)
    lon = forms.FloatField(required=True)

class AddAlbumForm(forms.Form):
    name = forms.CharField(max_length=255, required=True)
    description = forms.CharField(widget=forms.Textarea, required=False)

class PublicPhotoUploadForm(forms.Form):
    institution = forms.CharField(max_length=255, required=False)
    number = forms.CharField(max_length=100, required=False)
    title = forms.CharField(max_length=255, required=False)
    description = forms.CharField(max_length=2047, required=False)
    date = forms.CharField(max_length=100, required=False)
    url = forms.CharField(max_length=1023, required=False)
    licence = forms.CharField(max_length=255, required=False)