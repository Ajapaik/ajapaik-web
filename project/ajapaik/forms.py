import autocomplete_light
from django import forms
from .models import Area, Album, Photo, GeoTag, PhotoLike, Profile, Dating, Video, Licence
from django.utils.translation import ugettext_lazy as _
from haystack.forms import SearchForm


class APILoginForm(forms.Form):
    type = forms.CharField(max_length=255)
    username = forms.CharField(max_length=255)
    password = forms.CharField(max_length=255)
    version = forms.FloatField(required=False)
    length = forms.IntegerField(required=False, initial=0)
    os = forms.CharField(max_length=255, required=False, initial='android')


class APIAuthForm(forms.Form):
    _s = forms.CharField(max_length=255)
    _u = forms.IntegerField()
    _l = forms.CharField(max_length=2, required=False)
    _v = forms.FloatField(required=False)


# TODO: Make forms for everything, there's too much individual POST variable checking
class AreaSelectionForm(forms.Form):
    area = forms.ModelChoiceField(queryset=Area.objects.all(), label=_('Choose area'), )


class AlbumSelectionForm(forms.Form):
    album = forms.ModelChoiceField(queryset=Album.objects.filter(atype=Album.CURATED, is_public=True)
                                   .order_by('-created').all(), label=_('Choose album'),
                                   initial={'album': Album.objects.filter(is_public=True).order_by('-created')[0]})


class AlbumSelectionFilteringForm(forms.Form):
    q = forms.CharField(required=False)
    page = forms.IntegerField(min_value=1, initial=1, required=False)


class GalleryFilteringForm(forms.Form):
    album = forms.ModelChoiceField(queryset=Album.objects.all(), required=False)
    photo = forms.ModelChoiceField(queryset=Photo.objects.filter(rephoto_of__isnull=True), required=False)
    photos = forms.CharField(required=False)
    page = forms.IntegerField(min_value=1, initial=1, required=False)
    order1 = forms.ChoiceField(choices=[('amount', 'amount'), ('time', 'time'), ('closest', 'closest')], initial='time',
                               required=False)
    order2 = forms.ChoiceField(
        choices=[('comments', 'comments'), ('geotags', 'geotags'), ('rephotos', 'rephotos'), ('views', 'views'),
                 ('likes', 'likes'), ('added', 'added'), ('datings', 'datings'), ('stills', 'stills')], initial='added',
        required=False)
    order3 = forms.ChoiceField(choices=[('reverse', 'reverse'), ], initial=None, required=False)
    lat = forms.FloatField(min_value=-85.05115, max_value=85, required=False)
    lon = forms.FloatField(min_value=-180, max_value=180, required=False)
    q = forms.CharField(required=False)
    myLikes = forms.BooleanField(required=False)
    rephotosBy = forms.ModelChoiceField(queryset=Profile.objects.all(), required=False)

    def clean_page(self):
        page = self.cleaned_data['page']
        if page is None:
            return self.fields['page'].initial
        return page

    def clean_order1(self):
        order1 = self.cleaned_data['order1']
        if order1 is None:
            return self.fields['order1'].initial
        return order1

    def clean_order2(self):
        order2 = self.cleaned_data['order2']
        if order2 is None:
            return self.fields['order2'].initial
        return order2

    def clean_order3(self):
        order3 = self.cleaned_data['order3']
        if order3 is None:
            return self.fields['order3'].initial
        return order3


class HaystackPhotoSearchForm(SearchForm):
    def search(self):
        if not self.is_valid():
            return self.no_query_found()
        else:
            sqs = super(HaystackPhotoSearchForm, self).search().models(Photo)

        return sqs


class HaystackAlbumSearchForm(SearchForm):
    def search(self):
        sqs = super(HaystackAlbumSearchForm, self).search().models(Album)

        if not self.is_valid():
            return self.no_query_found()

        return sqs


class MapDataRequestForm(forms.Form):
    album = forms.ModelChoiceField(queryset=Album.objects.all(), label=_('Choose album'), required=False)
    area = forms.ModelChoiceField(queryset=Area.objects.all(), label=_('Choose area'), required=False)
    limit_by_album = forms.BooleanField(initial=False, required=False)
    sw_lat = forms.FloatField(min_value=-85.05115, max_value=85, required=False)
    sw_lon = forms.FloatField(min_value=-180, max_value=180, required=False)
    ne_lat = forms.FloatField(min_value=-85.05115, max_value=85, required=False)
    ne_lon = forms.FloatField(min_value=-180, max_value=180, required=False)
    starting = forms.DateField(required=False)
    ending = forms.DateField(required=False)


class GameAlbumSelectionForm(forms.Form):
    album = forms.ModelChoiceField(queryset=Album.objects.all(), label=_('Choose album'))


class GamePhotoSelectionForm(forms.Form):
    photo = forms.ModelChoiceField(queryset=Photo.objects.filter(rephoto_of__isnull=True), label=_('Choose photo'))


class GameNextPhotoForm(forms.Form):
    album = forms.ModelChoiceField(queryset=Album.objects.all(), label=_('Choose album'), required=False)
    area = forms.ModelChoiceField(queryset=Area.objects.all(), label=_('Choose area'), required=False)
    photo = forms.ModelChoiceField(queryset=Photo.objects.filter(rephoto_of__isnull=True),
                                   label=_('Choose photo'), required=False)


class CuratorAlbumSelectionForm(forms.Form):
    album = forms.ModelChoiceField(queryset=Album.objects.filter(
            atype=Album.CURATED
    ), label=_('Choose album'))

    # Should do ownership checking here, but it seems to be left to hacks
    # http://stackoverflow.com/questions/10422791/django-form-validation-with-authenticated-user-as-a-field
    def __init__(self, *args, **kwargs):
        super(CuratorAlbumSelectionForm, self).__init__(*args, **kwargs)


class CuratorAlbumEditForm(forms.Form):
    name = forms.CharField(max_length=255, required=True)
    description = forms.CharField(max_length=2047, required=False)
    open = forms.BooleanField(initial=False, required=False)
    is_public = forms.BooleanField(initial=False, required=False)
    parent_album = forms.ModelChoiceField(queryset=Album.objects.filter(
            atype=Album.CURATED, subalbum_of__isnull=True,
            is_public=True, open=True
    ), label=_('Choose parent album'), required=False)
    areaLat = forms.FloatField(min_value=-85.05115, max_value=85, required=False)
    areaLng = forms.FloatField(min_value=-180, max_value=180, required=False)


class AddAreaForm(forms.Form):
    name = forms.CharField(max_length=255, required=True)
    lat = forms.FloatField(required=True)
    lon = forms.FloatField(required=True)


class AddAlbumForm(forms.Form):
    name = forms.CharField(max_length=255, required=True)
    description = forms.CharField(widget=forms.Textarea, required=False)
    open = forms.BooleanField(required=False, initial=False)
    is_public = forms.BooleanField(initial=False, required=False)
    parent_album = forms.ModelChoiceField(queryset=Album.objects.filter(
            atype=Album.CURATED, subalbum_of__isnull=True,
            is_public=True, open=True
    ), label=_('Choose parent album'), required=False)


class PublicPhotoUploadForm(forms.Form):
    institution = forms.CharField(max_length=255, required=False)
    number = forms.CharField(max_length=100, required=False)
    title = forms.CharField(max_length=255, required=False)
    description = forms.CharField(max_length=2047, required=False)
    date = forms.CharField(max_length=100, required=False)
    url = forms.CharField(max_length=1023, required=False)
    licence = forms.CharField(max_length=255, required=False)


class CuratorPhotoUploadForm(forms.Form):
    id = forms.CharField(max_length=100)
    title = forms.CharField(required=False)
    creators = forms.CharField(max_length=255, required=False)
    imageUrl = forms.CharField()
    institution = forms.CharField(max_length=255, required=False)
    urlToRecord = forms.CharField(max_length=1023, required=False)
    identifyingNumber = forms.CharField(max_length=100)
    collections = forms.CharField(max_length=255, required=False)
    date = forms.CharField(max_length=255, required=False)
    types = forms.CharField(max_length=255, required=False)
    keywords = forms.CharField(max_length=3000, required=False)
    flip = forms.BooleanField(required=False)
    invert = forms.BooleanField(required=False)
    stereo = forms.BooleanField(required=False)
    rotated = forms.FloatField(min_value=0, max_value=270, required=False)
    latitude = forms.FloatField(min_value=-85.05115, max_value=85, required=False)
    longitude = forms.FloatField(min_value=-180, max_value=180, required=False)


class SelectionUploadForm(forms.Form):
    selection = forms.CharField(max_length=100000)
    album = forms.ModelChoiceField(queryset=Album.objects.filter(
            atype=Album.CURATED,
    ), label=_('Choose album'), required=False)
    parent_album = forms.ModelChoiceField(queryset=Album.objects.filter(
            atype=Album.CURATED, subalbum_of__isnull=True
    ), label=_('Choose parent album'), required=False)
    name = forms.CharField(max_length=255, required=False)
    description = forms.CharField(max_length=2047, required=False)
    open = forms.BooleanField(initial=False, required=False)
    public = forms.BooleanField(initial=False, required=False)
    areaLat = forms.FloatField(min_value=-85.05115, max_value=85, required=False)
    areaLng = forms.FloatField(min_value=-180, max_value=180, required=False)


class ApiRegisterForm(forms.Form):
    type = forms.CharField(max_length=255)
    username = forms.CharField(max_length=255)
    password = forms.CharField(max_length=255)
    length = forms.IntegerField(required=False, initial=0)
    os = forms.CharField(max_length=255, required=False, initial='android')


class SubmitGeotagForm(forms.ModelForm):
    class Meta:
        model = GeoTag
        exclude = ('user', 'trustworthiness')


class ConfirmGeotagForm(forms.Form):
    photo = forms.ModelChoiceField(queryset=Photo.objects.filter(rephoto_of__isnull=True))


class FrontpagePagingForm(forms.Form):
    album = forms.ModelChoiceField(queryset=Album.objects.filter(is_public=True), required=False)
    page = forms.IntegerField(min_value=1, required=False)


class ApiAlbumNearestForm(forms.Form):
    id = forms.ModelChoiceField(queryset=Album.objects.filter(is_public=True), required=False)
    latitude = forms.FloatField(min_value=-85.05115, max_value=85)
    longitude = forms.FloatField(min_value=-180, max_value=180)
    range = forms.FloatField(required=False)
    state = forms.CharField(max_length=255, required=False)


class ApiAlbumStateForm(forms.Form):
    id = forms.ModelChoiceField(queryset=Album.objects.filter(is_public=True))
    state = forms.CharField(max_length=255, required=False)


class ApiPhotoUploadForm(forms.Form):
    id = forms.ModelChoiceField(queryset=Photo.objects.filter(rephoto_of__isnull=True))
    latitude = forms.FloatField(min_value=-85.05115, max_value=85, required=False)
    longitude = forms.FloatField(min_value=-180, max_value=180, required=False)
    accuracy = forms.FloatField(min_value=0, required=False)
    age = forms.FloatField(min_value=0, required=False)
    date = forms.CharField(max_length=30)
    scale = forms.FloatField()
    yaw = forms.FloatField()
    pitch = forms.FloatField()
    roll = forms.FloatField()
    original = forms.FileField()
    flip = forms.IntegerField(min_value=0, max_value=1)


class ApiPhotoStateForm(forms.Form):
    id = forms.ModelChoiceField(queryset=Photo.objects.filter(rephoto_of__isnull=True))


class ApiUserMeForm(forms.Form):
    state = forms.CharField(max_length=255, required=False)


class PhotoSelectionForm(forms.Form):
    id = forms.ModelChoiceField(queryset=Photo.objects.all(), required=False)
    clear = forms.BooleanField(initial=False, required=False)


class PhotoLikeForm(forms.ModelForm):
    class Meta:
        model = PhotoLike
        fields = ('photo',)


class AlbumInfoModalForm(forms.Form):
    album = forms.ModelChoiceField(queryset=Album.objects.filter(atype=Album.CURATED))
    linkToGame = forms.BooleanField(required=False)
    linkToMap = forms.BooleanField(required=False)
    linkToGallery = forms.BooleanField(required=False)
    fbShareGame = forms.BooleanField(required=False)
    fbShareMap = forms.BooleanField(required=False)
    fbShareGallery = forms.BooleanField(required=False)


class DatingSubmitForm(forms.ModelForm):
    class Meta:
        model = Dating
        exclude = ('created', 'modified')

    def __init__(self, *args, **kwargs):
        super(DatingSubmitForm, self).__init__(*args, **kwargs)
        self.fields['start'].required = False
        self.fields['end'].required = False


class DatingConfirmForm(forms.Form):
    id = forms.ModelChoiceField(queryset=Dating.objects.all())


class VideoStillCaptureForm(forms.Form):
    video = forms.ModelChoiceField(queryset=Video.objects.all())
    album = forms.ModelChoiceField(queryset=Album.objects.filter(atype=Album.CURATED))
    timestamp = forms.IntegerField()


class PhotoUploadChoiceForm(forms.Form):
    action = forms.ChoiceField(choices=[
        ('import', _('Import from museum')),
        ('upload', _('Upload yourself'))
    ])


class UserPhotoUploadForm(autocomplete_light.ModelForm):
    # TODO: Add source
    albums = autocomplete_light.ModelMultipleChoiceField('PublicAlbumAutocomplete', required=False)
    licence = forms.ModelChoiceField(queryset=Licence.objects.filter(is_public=True))

    class Meta:
        model = Photo
        fields = ('image', 'description', 'author', 'licence', 'albums')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 1, 'cols': 40}),
        }


class UserPhotoUploadAddAlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ('name', 'description', 'is_public', 'open')
