from django import forms
from .models import Area, Album, Profile
from django.utils.translation import ugettext_lazy as _
from project import settings

# TODO: Make forms for everything, there's too much Javascript POST checking
class AreaSelectionForm(forms.Form):
    area = forms.ModelChoiceField(queryset=Area.objects.order_by('name').all(), label=_('Choose area'),
                                  initial=Area.objects.filter(pk=settings.DEFAULT_AREA_ID))

    def __init__(self, *args, **kwargs):
        super(AreaSelectionForm, self).__init__(*args, **kwargs)


class AlbumSelectionForm(forms.Form):
    album = forms.ModelChoiceField(queryset=Album.objects.filter(atype=Album.CURATED, is_public=True).all(),
                                   label=_('Choose album'), initial=Album.objects.filter(pk=settings.DEFAULT_ALBUM_ID))

    def __init__(self, *args, **kwargs):
        super(AlbumSelectionForm, self).__init__(*args, **kwargs)


class GameAlbumSelectionForm(forms.Form):
    album = forms.ModelChoiceField(queryset=Album.objects.all(), label=_('Choose album'),
                                   initial=Album.objects.filter(pk=settings.DEFAULT_ALBUM_ID))

    def __init__(self, *args, **kwargs):
        super(GameAlbumSelectionForm, self).__init__(*args, **kwargs)


class CuratorAlbumSelectionForm(forms.Form):
    album = forms.ModelChoiceField(queryset=Album.objects.filter(
        atype=Album.CURATED,
        is_public=True,
    ), label=_('Choose album'))

    # Should do ownership checking here, but it seems to be left to hacks
    # http://stackoverflow.com/questions/10422791/django-form-validation-with-authenticated-user-as-a-field
    def __init__(self, *args, **kwargs):
        super(CuratorAlbumSelectionForm, self).__init__(*args, **kwargs)


class AddAreaForm(forms.Form):
    name = forms.CharField(max_length=255, required=True)
    lat = forms.FloatField(required=True)
    lon = forms.FloatField(required=True)


class AddAlbumForm(forms.Form):
    name = forms.CharField(max_length=255, required=True)
    description = forms.CharField(widget=forms.Textarea, required=False)
    #is_public_mutable = forms.CharField(required=True, initial=False)

class PublicPhotoUploadForm(forms.Form):
    institution = forms.CharField(max_length=255, required=False)
    number = forms.CharField(max_length=100, required=False)
    title = forms.CharField(max_length=255, required=False)
    description = forms.CharField(max_length=2047, required=False)
    date = forms.CharField(max_length=100, required=False)
    url = forms.CharField(max_length=1023, required=False)
    licence = forms.CharField(max_length=255, required=False)


class CuratorPhotoUploadForm(forms.Form):
    title = forms.CharField(required=False)
    creators = forms.CharField(max_length=255, required=False)
    imageUrl = forms.CharField()
    institution = forms.CharField(max_length=255, required=False)
    urlToRecord = forms.CharField(max_length=1023, required=False)
    identifyingNumber = forms.CharField(max_length=100)
    date = forms.CharField(max_length=100, required=False)
    types = forms.CharField(max_length=255, required=False)
    flip = forms.BooleanField(required=False)
    invert = forms.BooleanField(required=False)
    stereo = forms.BooleanField(required=False)
