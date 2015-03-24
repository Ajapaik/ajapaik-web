from django import forms
from .models import Area, Album, CatTag, CatAlbum, CatPhoto, Profile, Photo, GeoTag
from django.utils.translation import ugettext_lazy as _
from project import settings


# TODO: Make forms for everything, there's too much Javascript POST variable checking
class AreaSelectionForm(forms.Form):
    area = forms.ModelChoiceField(queryset=Area.objects.all(), label=_('Choose area'),
                                  initial=Area.objects.filter(pk=settings.DEFAULT_AREA_ID))

    def __init__(self, *args, **kwargs):
        super(AreaSelectionForm, self).__init__(*args, **kwargs)


class AlbumSelectionForm(forms.Form):
    album = forms.ModelChoiceField(queryset=Album.objects.filter(atype=Album.CURATED, is_public=True)
                                   .order_by('-created').all(), label=_('Choose album'),
                                   initial=Album.objects.filter(pk=settings.DEFAULT_ALBUM_ID))

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


class CuratorAlbumEditForm(forms.Form):
    name = forms.CharField(max_length=255, required=True)
    description = forms.CharField(max_length=2047, required=False)


class AddAreaForm(forms.Form):
    name = forms.CharField(max_length=255, required=True)
    lat = forms.FloatField(required=True)
    lon = forms.FloatField(required=True)


class AddAlbumForm(forms.Form):
    name = forms.CharField(max_length=255, required=True)
    description = forms.CharField(widget=forms.Textarea, required=False)
    # is_public_mutable = forms.CharField(required=True, initial=False)


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


class CatLoginForm(forms.Form):
    type = forms.CharField(max_length=255, required=False)
    username = forms.CharField(max_length=40)
    password = forms.CharField(max_length=64)
    length = forms.IntegerField(required=False, initial=0)
    os = forms.CharField(max_length=255, required=False, initial='android')


class CatAuthForm(forms.Form):
    _s = forms.CharField(max_length=255)
    _u = forms.IntegerField()


class CatAlbumStateForm(forms.Form):
    id = forms.ModelChoiceField(queryset=CatAlbum.objects.all())
    max = forms.IntegerField(required=False)
    state = forms.CharField(max_length=255, required=False)


class CatTagForm(forms.Form):
    id = forms.ModelChoiceField(queryset=CatAlbum.objects.all())
    photo = forms.ModelChoiceField(queryset=CatPhoto.objects.all())
    tag = forms.ModelChoiceField(queryset=CatTag.objects.all(), to_field_name='name')
    value = forms.TypedChoiceField(choices=[(-1, -1), (0, 0), (1, 1)], coerce=int)
    state = forms.CharField(max_length=255, required=False)


class CatFavoriteForm(forms.Form):
    album = forms.ModelChoiceField(queryset=CatAlbum.objects.all())
    photo = forms.ModelChoiceField(queryset=CatPhoto.objects.all())
    state = forms.CharField(max_length=255, required=False)


class SubmitGeotagForm(forms.ModelForm):
    class Meta:
        model = GeoTag
        exclude = ('user', 'trustworthiness')