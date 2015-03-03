from django import forms
from .models import Area, Album
from django.utils.translation import ugettext_lazy as _
from project import settings

# TODO: Make forms for everything, there's too much Javascript going on right now
class AreaSelectionForm(forms.Form):
    area = forms.ModelChoiceField(queryset=Area.objects.order_by('name').all(), label=_('Choose area'), initial=Area.objects.filter(pk=settings.DEFAULT_AREA_ID))

    def __init__(self, *args, **kwargs):
        super(AreaSelectionForm, self).__init__(*args, **kwargs)

class AlbumSelectionForm(forms.Form):
    album = forms.ModelChoiceField(queryset=Album.objects.all(), label=_('Choose album'), initial=Album.objects.filter(pk=settings.DEFAULT_ALBUM_ID))

    def __init__(self, *args, **kwargs):
        super(AlbumSelectionForm, self).__init__(*args, **kwargs)

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

class CuratorPhotoUploadForm(forms.Form):
    description = forms.CharField(required=False)
    author = forms.CharField(max_length=255, required=False)
    image_url = forms.CharField()
    source = forms.CharField(max_length=255, required=False)
    source_url = forms.CharField(max_length=1023, required=False)
    source_key = forms.CharField(max_length=100)
    date_text = forms.CharField(max_length=100, required=False)
