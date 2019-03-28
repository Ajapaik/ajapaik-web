import autocomplete_light
from django import forms
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django_comments import get_model
from django_comments_xtd.conf.defaults import COMMENT_MAX_LENGTH
from django_comments_xtd.forms import XtdCommentForm
from registration.forms import RegistrationFormUniqueEmail

from .models import Area, Album, Photo, GeoTag, PhotoLike, Profile, Dating, \
    Video, Licence


class UserRegistrationForm(RegistrationFormUniqueEmail):
    username = forms.CharField(max_length=254, required=False, widget=forms.HiddenInput())
    first_name = forms.CharField(label=_('First name'), max_length=30)
    last_name = forms.CharField(label=_('Last name'), max_length=30)

    def clean_email(self):
        email = self.cleaned_data['email']
        self.cleaned_data['username'] = email
        return email


class APILoginAuthForm(forms.Form):
    type = forms.CharField(max_length=255)
    username = forms.CharField(max_length=255)
    # For Google+ oAuth
    password = forms.CharField(max_length=2048)
    version = forms.FloatField(required=False)
    length = forms.IntegerField(required=False, initial=0)
    os = forms.CharField(max_length=255, required=False, initial='android')
    firstname = forms.CharField(max_length=255, required=False)
    lastname = forms.CharField(max_length=255, required=False)


class APIAuthForm(forms.Form):
    _s = forms.CharField(max_length=255)
    _u = forms.IntegerField()
    _l = forms.CharField(max_length=2, required=False)
    _v = forms.FloatField(required=False)


# TODO: Make forms for everything, there's too much individual POST variable checking
class AreaSelectionForm(forms.Form):
    area = forms.ModelChoiceField(queryset=Area.objects.all(), label=_('Choose area'), )


class AlbumSelectionForm(forms.Form):
    album = forms.ModelChoiceField(
        queryset=Album.objects.filter(atype=Album.CURATED, is_public=True).order_by('-created').all(),
        label=_('Choose album'),
        # initial={'album': Album.objects.filter(is_public=True).order_by('-created').first()}
    )


class AlbumSelectionFilteringForm(forms.Form):
    q = forms.CharField(required=False)
    page = forms.IntegerField(min_value=1, initial=1, required=False)
    people = forms.BooleanField(initial=False, required=False)


class GalleryFilteringForm(forms.Form):
    album = forms.ModelChoiceField(queryset=Album.objects.all(), required=False)
    photo = forms.ModelChoiceField(queryset=Photo.objects.filter(rephoto_of__isnull=True), required=False)
    photos = forms.CharField(required=False)
    page = forms.IntegerField(min_value=1, initial=1, required=False)
    order1 = forms.ChoiceField(choices=[('amount', 'amount'), ('time', 'time'), ('closest', 'closest')], initial='time',
                               required=False)
    order2 = forms.ChoiceField(
        choices=[('comments', 'comments'), ('geotags', 'geotags'), ('rephotos', 'rephotos'), ('views', 'views'),
                 ('likes', 'likes'), ('added', 'added'), ('datings', 'datings'), ('stills', 'stills')],
        initial='added',
        required=False)
    order3 = forms.ChoiceField(choices=[('reverse', 'reverse'), ], initial=None, required=False)
    lat = forms.FloatField(min_value=-85.05115, max_value=85, required=False)
    lon = forms.FloatField(min_value=-180, max_value=180, required=False)
    q = forms.CharField(required=False)
    myLikes = forms.BooleanField(required=False)
    rephotosBy = forms.ModelChoiceField(queryset=Profile.objects.all(), required=False)
    people = forms.BooleanField(initial=False, required=False)

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
    count_limit = forms.IntegerField(min_value=1, required=False)


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
    licence = forms.CharField(max_length=255, required=False)


class SelectionUploadForm(forms.Form):
    selection = forms.CharField(max_length=100000)


class SubmitGeotagForm(forms.ModelForm):
    class Meta:
        model = GeoTag
        exclude = ('user', 'trustworthiness')


class ConfirmGeotagForm(forms.Form):
    photo = forms.ModelChoiceField(queryset=Photo.objects.filter(rephoto_of__isnull=True))


class FrontpagePagingForm(forms.Form):
    album = forms.ModelChoiceField(queryset=Album.objects.filter(is_public=True), required=False)
    page = forms.IntegerField(min_value=1, required=False)


class ApiAlbumNearestPhotosForm(forms.Form):
    id = forms.ModelChoiceField(queryset=Album.objects.filter(is_public=True), required=False)
    latitude = forms.FloatField(min_value=-85.05115, max_value=85)
    longitude = forms.FloatField(min_value=-180, max_value=180)
    range = forms.FloatField(required=False)
    start = forms.IntegerField(required=False)
    limit = forms.IntegerField(required=False)


class ApiFinnaNearestPhotosForm(forms.Form):
    id = forms.ModelChoiceField(queryset=Album.objects.filter(is_public=True), required=False)
    latitude = forms.FloatField(min_value=-85.05115, max_value=85)
    longitude = forms.FloatField(min_value=-180, max_value=180)
    range = forms.FloatField(required=False)
    start = forms.IntegerField(required=False)
    limit = forms.IntegerField(required=False)
    query = forms.CharField(max_length=255, required=False)
    album = forms.CharField(max_length=255, required=False)


class ApiAlbumStateForm(forms.Form):
    id = forms.ModelChoiceField(queryset=Album.objects.filter(is_public=True))
    state = forms.CharField(max_length=255, required=False)
    start = forms.IntegerField(required=False)
    limit = forms.IntegerField(required=False)


class ApiAlbumSourceForm(forms.Form):
    query = forms.CharField(max_length=255, required=True)
    start = forms.IntegerField(required=False)
    limit = forms.IntegerField(required=False)


class ApiPhotoUploadForm(forms.Form):
    id = forms.CharField(max_length=255)
    latitude = forms.FloatField(min_value=-85.05115, max_value=85, required=False)
    longitude = forms.FloatField(min_value=-180, max_value=180, required=False)
    accuracy = forms.FloatField(min_value=0, required=False)
    age = forms.FloatField(min_value=0, required=False)

    # We expecting here a date but in model we have datetime field. So to do
    # less work we define here DateTimeField.
    date = forms.DateTimeField(input_formats=['%d-%m-%Y'])
    scale = forms.FloatField()
    yaw = forms.FloatField()
    pitch = forms.FloatField()
    roll = forms.FloatField()
    flip = forms.BooleanField(required=False)
    original = forms.FileField()


class ApiPhotoStateForm(forms.Form):
    id = forms.IntegerField()  # Photo id


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
        ('import', _('Import from public collections')),
        ('upload', _('Upload yourself'))
    ])


class UserPhotoUploadForm(autocomplete_light.shortcuts.ModelForm):
    albums = autocomplete_light.shortcuts.ModelMultipleChoiceField('PublicAlbumAutocomplete', label=_('Albums'), required=True)
    licence = forms.ModelChoiceField(label=_('Licence'), queryset=Licence.objects.filter(is_public=True),
                                     required=False)
    uploader_is_author = forms.BooleanField(label=_('I am the author'), required=False)

    class Meta:
        model = Photo
        fields = ('image', 'description', 'author', 'uploader_is_author', 'licence', 'albums')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 1, 'cols': 40})
        }

    def clean(self):
        super(UserPhotoUploadForm, self).clean()
        if not self.cleaned_data.get('image'):
            self.errors['image'] = [_('Missing image')]
        if not self.cleaned_data.get('description'):
            self.errors['description'] = [_('Missing description')]
        if not self.cleaned_data.get('uploader_is_author') and not self.cleaned_data.get('licence'):
            self.errors['licence'] = [_('Missing licence')]


class UserPhotoUploadAddAlbumForm(forms.ModelForm):
    location = forms.CharField(max_length=255, required=False)

    class Meta:
        model = Album
        fields = ('atype', 'subalbum_of', 'name', 'description', 'is_public', 'open', 'location', 'lat', 'lon')

    def __init__(self, *args, **kwargs):
        # TODO: Show person fields if applicable
        self.profile = kwargs.pop('profile', None)
        super(UserPhotoUploadAddAlbumForm, self).__init__(*args, **kwargs)
        self.fields['subalbum_of'].label = _('Parent album')
        self.fields['subalbum_of'].queryset = Album.objects.filter(atype=Album.CURATED) \
            .filter(Q(open=True) | Q(profile=self.profile))
        self.fields['location'].help_text = _('If this album is tied to a certain location, specify here')
        self.fields['lat'].widget = forms.HiddenInput()
        self.fields['lon'].widget = forms.HiddenInput()
        self.fields['atype'].label = _('Album type')
        self.fields['atype'].choices = [(Album.PERSON, _('Person')), (Album.CURATED, _('Anything else'))]


class CuratorWholeSetAlbumsSelectionForm(forms.Form):
    albums = autocomplete_light.shortcuts.ModelMultipleChoiceField('PublicAlbumAutocomplete', label=_('Albums'), required=True)

    def __init__(self, *args, **kwargs):
        super(CuratorWholeSetAlbumsSelectionForm, self).__init__(*args, **kwargs)

        self.fields['albums'].help_text = None


class CommentForm(XtdCommentForm):
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['comment'] = forms.CharField(
            widget=forms.Textarea(
                attrs={
                    'placeholder': _(
                        'Comment box supports Markdown\n\n'

                        'Paragraphs\n'
                        'Add two new lines to start a new paragraph.\n\n'

                        'Bold\n'
                        '**Geotagging** is the first task on Ajapaik.\n\n'

                        'Italic\n'
                        'Next come *rephotography* and *dating*.\n\n'

                        'Links\n'
                        'Join the discussion on [Ajapaiklejad FB group]'
                        '(https://www.facebook.com/groups/ajapaiklejad).\n\n'

                        'Images\n'
                        '![Ajapaik is gift for EV100]'
                        '(https://ajapaik.ee/static/images/ev100.png)'
                    )
                }
            ),
            max_length=COMMENT_MAX_LENGTH)


class EditCommentForm(forms.Form):
    comment_id = forms.IntegerField()
    text = forms.CharField()

    def clean_comment_id(self):
        self.comment = get_object_or_404(
            get_model(), pk=self.cleaned_data['comment_id']
        )

    def clean(self):
        text = self.cleaned_data['text']
        if self.comment.comment == self.cleaned_data['text']:
            forms.ValidationError(_('Nothing to change.'), code='same_text')


class ApiFetchFinnaPhoto(forms.Form):
    id = forms.CharField(max_length=255)

class ApiToggleFavoritePhotoForm(forms.Form):
    id = forms.CharField(max_length=255)
    favorited = forms.BooleanField(required=False)


class ApiFavoritedPhotosForm(forms.Form):
    latitude = forms.FloatField(min_value=-85.05115, max_value=85)
    longitude = forms.FloatField(min_value=-180, max_value=180)
    start = forms.IntegerField(required=False)
    limit = forms.IntegerField(required=False)


class ApiPhotoSearchForm(forms.Form):
    query = forms.CharField()
    rephotosOnly = forms.BooleanField(required=False, initial=False)


class ApiPhotoInAlbumSearchForm(forms.Form):
    query = forms.CharField()
    albumId = forms.ModelChoiceField(queryset=Album.objects.all())
    rephotosOnly = forms.BooleanField(required=False, initial=False)


class ApiUserRephotoSearchForm(forms.Form):
    query = forms.CharField()


class ApiUserRephotosForm(forms.Form):
    start = forms.IntegerField(required=False)
    limit = forms.IntegerField(required=False)


class ApiAlbumSearchForm(forms.Form):
    query = forms.CharField()
