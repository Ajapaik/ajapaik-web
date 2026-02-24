from allauth.account.forms import SignupForm as AllauthSignupForm
from django_recaptcha.fields import ReCaptchaField

from dal import autocomplete
from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_comments_xtd.conf.defaults import COMMENT_MAX_LENGTH
from django_comments_xtd.forms import XtdCommentForm

from .models import (Album, Area, Dating, GeoTag, Photo, PhotoLike,
                     Profile, Video)


class OauthDoneForm(forms.Form):
    token = forms.CharField(label=_('Token'), max_length=254)
    route = forms.CharField(label=_('Route'), max_length=254)
    provider = forms.CharField(label=_('Provider'), max_length=254)


class SignupForm(AllauthSignupForm):
    email = forms.CharField(label=_('Email'), max_length=254)
    first_name = forms.CharField(label=_('First name'), max_length=30)
    last_name = forms.CharField(label=_('Last name'), max_length=30)
    password1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Password confirmation'), widget=forms.PasswordInput)
    captcha = ReCaptchaField()

    field_order = ['email', 'first_name', 'last_name', 'password1', 'password2', 'captcha']

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user


class APILoginForm(forms.Form):
    LOGIN_TYPE_AUTO = 'auto'
    LOGIN_TYPE_AJAPAIK = 'ajapaik'
    LOGIN_TYPE_GOOGLE = 'google'
    LOGIN_TYPE_GOOGLE2 = 'google2'
    LOGIN_TYPE_FACEBOOK = 'fb'
    LOGIN_TYPE_WIKIMEDIA_COMMONS = 'wikimedia-commons'
    LOGIN_TYPES = [
        (LOGIN_TYPE_AUTO, 'Auto'),  # Create and login new user if not found.
        # This deprecated behaviour before
        # django-allauth integration.
        (LOGIN_TYPE_AJAPAIK, 'Ajapaik'),  # Usual email/password pair.
        (LOGIN_TYPE_GOOGLE, 'Google'),  # Google login.
        (LOGIN_TYPE_GOOGLE2, 'Google2'),  # Google login with access_token.
        (LOGIN_TYPE_FACEBOOK, 'Facebook'),  # FB user ID.
        (LOGIN_TYPE_WIKIMEDIA_COMMONS, 'Wikimedia Commons')
    ]

    OS_TYPE_ANDROID = 'android'
    OS_TYPES = [
        (OS_TYPE_ANDROID, 'Android'),
    ]

    type = forms.ChoiceField(choices=LOGIN_TYPES)
    username = forms.CharField(max_length=2048)
    password = forms.CharField(max_length=2048, required=False)
    version = forms.FloatField(required=False)
    length = forms.IntegerField(required=False, initial=0)
    os = forms.ChoiceField(
        choices=OS_TYPES,
        required=False,
        initial=OS_TYPE_ANDROID
    )


class APIRegisterForm(forms.Form):
    REGISTRATION_TYPE_AJAPAIK = 'ajapaik'
    REGISTRATION_TYPE_GOOGLE = 'google'
    REGISTRATION_TYPE_FACEBOOK = 'facebook'
    REGISTRATION_TYPE_WIKIMEDIA_COMMONS = 'wikimedia_commons'
    REGISTRATION_TYPES = [
        (REGISTRATION_TYPE_AJAPAIK, 'Ajapaik'),  # Usual email/password pair.
        (REGISTRATION_TYPE_GOOGLE, 'Google'),  # Google login.
        (REGISTRATION_TYPE_FACEBOOK, 'Facebook'),  # FB user ID.
        (REGISTRATION_TYPE_WIKIMEDIA_COMMONS, 'WikimediaCommons')
    ]

    OS_TYPE_ANDROID = 'android'
    OS_TYPES = [
        (OS_TYPE_ANDROID, 'Android'),
    ]

    type = forms.ChoiceField(choices=REGISTRATION_TYPES)
    username = forms.CharField(max_length=255)
    password = forms.CharField(max_length=1105)
    firstname = forms.CharField(max_length=255)
    lastname = forms.CharField(max_length=255)
    length = forms.IntegerField(required=False, initial=0)
    os = forms.ChoiceField(
        required=False,
        choices=OS_TYPES,
        initial=OS_TYPE_ANDROID
    )


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
    collections = forms.BooleanField(initial=False, required=False)
    film = forms.BooleanField(initial=False, required=False)


class BaseFilteringForm(forms.Form):
    # Filtering
    q = forms.CharField(max_length=255, required=False)
    people = forms.BooleanField(initial=False, required=False)
    backsides = forms.BooleanField(initial=False, required=False)
    interiors = forms.BooleanField(initial=False, required=False)
    exteriors = forms.BooleanField(initial=False, required=False)
    ground_viewpoint_elevation = forms.BooleanField(initial=False, required=False)
    raised_viewpoint_elevation = forms.BooleanField(initial=False, required=False)
    aerial_viewpoint_elevation = forms.BooleanField(initial=False, required=False)
    no_geotags = forms.BooleanField(initial=False, required=False)
    high_quality = forms.BooleanField(initial=False, required=False)
    portrait = forms.BooleanField(initial=False, required=False)
    square = forms.BooleanField(initial=False, required=False)
    landscape = forms.BooleanField(initial=False, required=False)
    panoramic = forms.BooleanField(initial=False, required=False)
    date_from = forms.DateField(initial=None, required=False)
    date_to = forms.DateField(initial=None, required=False)

    # Sorting
    order1 = forms.ChoiceField(initial='time', choices=[('amount', 'amount'), ('time', 'time'), ('closest', 'closest')],
                               required=False)
    order2 = forms.ChoiceField(initial='added',
                               choices=[('comments', 'comments'), ('geotags', 'geotags'), ('rephotos', 'rephotos'),
                                        ('views', 'views'),
                                        ('likes', 'likes'), ('added', 'added'), ('datings', 'datings'),
                                        ('stills', 'stills'),
                                        ('transcriptions', 'transcriptions'), ('annotations', 'annotations'),
                                        ('similar_photos', 'similar_photos')],
                               required=False)
    order3 = forms.ChoiceField(choices=[('reverse', 'reverse'), ], initial=None, required=False)


class GalleryFilteringForm(BaseFilteringForm):
    album = forms.ModelChoiceField(queryset=Album.objects.all(), required=False)
    photo = forms.ModelChoiceField(queryset=Photo.objects.filter(rephoto_of__isnull=True), required=False)
    page = forms.IntegerField(min_value=1, initial=1, required=False)
    lat = forms.FloatField(min_value=-85.05115, max_value=85, required=False)
    lon = forms.FloatField(min_value=-180, max_value=180, required=False)
    myLikes = forms.BooleanField(required=False)
    collections = forms.IntegerField(required=False)
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
    album_id = forms.IntegerField()
    name = forms.CharField(max_length=255, required=True)
    description = forms.CharField(max_length=2047, required=False)
    open = forms.BooleanField(initial=False, required=False)
    is_public = forms.BooleanField(initial=False, required=False)
    parent_album_id = forms.IntegerField(required=False)
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
    licenceUrl = forms.CharField(max_length=255, required=False)
    persons = forms.JSONField(required=False)
    start_date = forms.CharField(max_length=27, required=False)
    end_date = forms.CharField(max_length=27, required=False)
    date_start_accuracy = forms.CharField(max_length=32, required=False)
    date_end_accuracy = forms.CharField(max_length=32, required=False)


class SelectionUploadForm(forms.Form):
    selection = forms.CharField(max_length=100000)


class SubmitGeotagForm(forms.ModelForm):
    class Meta:
        model = GeoTag
        exclude = ('user', 'trustworthiness')


class ConfirmGeotagForm(forms.Form):
    photo = forms.ModelChoiceField(queryset=Photo.objects.filter(rephoto_of__isnull=True))


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
    album = forms.ModelChoiceField(queryset=Album.objects.filter(Q(atype=Album.CURATED) | Q(atype=Album.COLLECTION)
                                                                 | Q(atype=Album.PERSON)))
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


class RephotoUploadSettingsForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('wikimedia_commons_rephoto_upload_consent',)
        labels = {
            'wikimedia_commons_rephoto_upload_consent': _('I wish to to upload my rephotos to Wikimedia Commons')
        }
        widgets = {
            'wikimedia_commons_rephoto_upload_consent': forms.Select(choices=[(True, _('Yes')), (False, _('No'))])
        }

    def clean(self):
        super(RephotoUploadSettingsForm, self).clean()
        if self.cleaned_data.get('wikimedia_commons_rephoto_upload_consent') is None:
            self.errors['wikimedia_commons_rephoto_upload_consent'] = [
                _('Please specify whether you would like your rephotos to be uploaded to Wikimedia Commons as well')]


class CuratorWholeSetAlbumsSelectionForm(forms.Form):
    albums = forms.ModelChoiceField(
        queryset=Album.objects.all(),
        required=True,
        widget=autocomplete.ModelSelect2(url='open-album-autocomplete')
    )

    def __init__(self, *args, **kwargs):
        super(CuratorWholeSetAlbumsSelectionForm, self).__init__(*args, **kwargs)

        self.fields['albums'].help_text = None


class CommentForm(XtdCommentForm):
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['email'] = forms.EmailField(label=_('Email address'), required=False)
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
    query = forms.CharField(required=False)
    rephotosOnly = forms.BooleanField(required=False, initial=False)
    latitude = forms.FloatField(min_value=-85.05115, max_value=85, required=False)
    longitude = forms.FloatField(min_value=-180, max_value=180, required=False)


class ApiPhotoInAlbumSearchForm(forms.Form):
    query = forms.CharField(required=False)
    albumId = forms.ModelChoiceField(queryset=Album.objects.all())
    rephotosOnly = forms.BooleanField(required=False, initial=False)
    latitude = forms.FloatField(min_value=-85.05115, max_value=85, required=False)
    longitude = forms.FloatField(min_value=-180, max_value=180, required=False)


class ApiUserRephotoSearchForm(forms.Form):
    query = forms.CharField(required=False)
    latitude = forms.FloatField(min_value=-85.05115, max_value=85, required=False)
    longitude = forms.FloatField(min_value=-180, max_value=180, required=False)


class ApiUserRephotosForm(forms.Form):
    start = forms.IntegerField(required=False)
    limit = forms.IntegerField(required=False)
    latitude = forms.FloatField(min_value=-85.05115, max_value=85, required=False)
    longitude = forms.FloatField(min_value=-180, max_value=180, required=False)


class ApiAlbumSearchForm(forms.Form):
    query = forms.CharField(required=False)


class ApiWikidocsAlbumsSearchForm(forms.Form):
    query = forms.CharField(required=False)
    language = forms.CharField(required=False)
    latitude = forms.FloatField(min_value=-85.05115, max_value=85, required=False)
    longitude = forms.FloatField(min_value=-180, max_value=180, required=False)
    start = forms.IntegerField(required=False)
    limit = forms.IntegerField(required=False)


class ApiWikidocsAlbumSearchForm(forms.Form):
    query = forms.CharField(required=False)
    id = forms.CharField(required=True)
    language = forms.CharField(required=False)
    latitude = forms.FloatField(min_value=-85.05115, max_value=85, required=False)
    longitude = forms.FloatField(min_value=-180, max_value=180, required=False)
    start = forms.IntegerField(required=False)
    limit = forms.IntegerField(required=False)


class CsvImportForm(forms.Form):
    zip_file = forms.FileField(required=False)
    csv_file = forms.FileField()
