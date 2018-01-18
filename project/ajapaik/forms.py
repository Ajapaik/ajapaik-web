import autocomplete_light
from django import forms
from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django_comments import get_model
from django_comments_xtd.forms import XtdCommentForm
from haystack.forms import SearchForm
from registration.forms import RegistrationFormUniqueEmail

from .models import Album, Photo, GeoTag, PhotoLike, Profile, Dating, Licence


class UserRegistrationForm(RegistrationFormUniqueEmail):
    username = forms.CharField(max_length=254, required=False, widget=forms.HiddenInput())

    def clean_email(self):
        email = self.cleaned_data['email']
        self.cleaned_data['username'] = email
        return email


class AlbumSelectionForm(forms.Form):
    album = forms.ModelChoiceField(queryset=Album.objects.filter(atype=Album.CURATED, is_public=True)
                                   .order_by('-created').all(), label=_('Choose album'))

    def __init__(self, *args, **kwargs):
        super(AlbumSelectionForm, self).__init__(*args, **kwargs)
        self.fields['album'].initial = {'album': Album.objects.filter(is_public=True).order_by('-created')[0]}


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
                 ('likes', 'likes'), ('added', 'added'), ('datings', 'datings'), ('stills', 'stills')],
        initial='added',
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


class PhotoUploadChoiceForm(forms.Form):
    action = forms.ChoiceField(choices=[
        ('import', _('Import from public collections')),
        ('upload', _('Upload yourself'))
    ])


class UserPhotoUploadForm(autocomplete_light.ModelForm):
    albums = autocomplete_light.ModelMultipleChoiceField('PublicAlbumAutocomplete', label=_('Albums'), required=False)
    licence = forms.ModelChoiceField(label=_('Licence'), queryset=Licence.objects.filter(is_public=True),
                                     required=False)
    uploader_is_author = forms.BooleanField(label=_('I am the author'), required=False)

    class Meta:
        model = Photo
        fields = ('image', 'title', 'description', 'author', 'uploader_is_author', 'licence', 'albums')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 1, 'cols': 40}),
        }

    def clean(self):
        super(UserPhotoUploadForm, self).clean()
        if not self.cleaned_data.get('image'):
            self.errors['image'] = [_('Missing image')]
        if not self.cleaned_data.get('title'):
            self.errors['title'] = [_('Missing title')]
        if not self.cleaned_data.get('description'):
            self.errors['description'] = [_('Missing description')]
        if not self.cleaned_data.get('uploader_is_author') and not self.cleaned_data.get('licence'):
            self.errors['licence'] = [_('Missing licence')]


class UserPhotoUploadAddAlbumForm(forms.ModelForm):
    location = forms.CharField(max_length=255, required=False)

    class Meta:
        model = Album
        fields = ('subalbum_of', 'name', 'description', 'is_public', 'open', 'location', 'lat', 'lon')

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop('profile', None)
        super(UserPhotoUploadAddAlbumForm, self).__init__(*args, **kwargs)
        self.fields['subalbum_of'].label = _('Parent album')
        self.fields['subalbum_of'].queryset = Album.objects.filter(atype=Album.CURATED) \
            .filter(Q(open=True) | Q(profile=self.profile))
        self.fields['location'].help_text = _('If this album is tied to a certain location, specify here')
        self.fields['lat'].widget = forms.HiddenInput()
        self.fields['lon'].widget = forms.HiddenInput()


class CuratorWholeSetAlbumsSelectionForm(forms.Form):
    albums = autocomplete_light.ModelMultipleChoiceField('PublicAlbumAutocomplete', label=_('Albums'), required=True)

    def __init__(self, *args, **kwargs):
        super(CuratorWholeSetAlbumsSelectionForm, self).__init__(*args, **kwargs)

        self.fields['albums'].help_text = None


class ResendActivationEmailForm(forms.Form):
    email = forms.EmailField(required=True)


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name')


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
            max_length=settings.COMMENT_MAX_LENGTH)


class EditCommentForm(forms.Form):
    comment_id = forms.IntegerField()
    text = forms.CharField()

    def clean_comment_id(self):
        self.comment = get_object_or_404(
            get_model(), pk=self.cleaned_data['comment_id']
        )

    def clean(self):
        if self.comment.comment == self.cleaned_data['text']:
            forms.ValidationError(_('Nothing to change.'), code='same_text')
