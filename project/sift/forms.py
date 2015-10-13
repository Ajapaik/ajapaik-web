from django import forms
from haystack.forms import SearchForm
from project.sift.models import CatPushDevice, CatPhoto, CatTag, CatAlbum


class CatLoginForm(forms.Form):
    type = forms.CharField(max_length=255)
    username = forms.CharField(max_length=255)
    password = forms.CharField(max_length=255)
    version = forms.FloatField(required=False)
    length = forms.IntegerField(required=False, initial=0)
    os = forms.CharField(max_length=255, required=False, initial='android')


class CatAuthForm(forms.Form):
    _s = forms.CharField(max_length=255)
    _u = forms.IntegerField()
    _l = forms.CharField(max_length=2, required=False)
    _v = forms.FloatField(required=False)


class CatPushRegisterForm(forms.ModelForm):
    class Meta:
        model = CatPushDevice
        fields = ('profile', 'type', 'token', 'filter')


class CatAlbumStateForm(forms.Form):
    id = forms.ModelChoiceField(queryset=CatAlbum.objects.all())
    max = forms.IntegerField(required=False)
    state = forms.CharField(max_length=255, required=False)


class CatTagForm(forms.Form):
    id = forms.ModelChoiceField(queryset=CatAlbum.objects.all())
    photo = forms.ModelChoiceField(queryset=CatPhoto.objects.all())
    tag = forms.ModelChoiceField(queryset=CatTag.objects.all(), to_field_name='name')
    value = forms.TypedChoiceField(choices=[(-1, -1), (0, 0), (1, 1)], coerce=int)
    source = forms.CharField(max_length=3, required=False)
    state = forms.CharField(max_length=255, required=False)


class CatFavoriteForm(forms.Form):
    album = forms.ModelChoiceField(queryset=CatAlbum.objects.all())
    photo = forms.ModelChoiceField(queryset=CatPhoto.objects.all())
    state = forms.CharField(max_length=255, required=False)


class CatResultsFilteringForm(forms.Form):
    CHOICES = ((1, 1), (0, 0), (-1, -1))
    interior_or_exterior = forms.MultipleChoiceField(choices=CHOICES, required=False)
    urban_or_rural = forms.MultipleChoiceField(choices=CHOICES, required=False)
    manmade_or_nature = forms.MultipleChoiceField(choices=CHOICES, required=False)
    view_or_social = forms.MultipleChoiceField(choices=CHOICES, required=False)
    ground_or_raised = forms.MultipleChoiceField(choices=CHOICES, required=False)
    one_or_many = forms.MultipleChoiceField(choices=CHOICES, required=False)
    whole_or_detail = forms.MultipleChoiceField(choices=CHOICES, required=False)
    staged_or_natural = forms.MultipleChoiceField(choices=CHOICES, required=False)
    public_or_private = forms.MultipleChoiceField(choices=CHOICES, required=False)
    album = forms.ModelChoiceField(queryset=CatAlbum.objects.all(), required=False)
    show_pictures = forms.BooleanField(required=False)
    page = forms.IntegerField(required=False)
    q = forms.CharField(required=False)


class CatTaggerAlbumSelectionForm(forms.Form):
    album = forms.ModelChoiceField(queryset=CatAlbum.objects.all())


class HaystackCatPhotoSearchForm(SearchForm):
    def search(self):
        sqs = super(HaystackCatPhotoSearchForm, self).search().models(CatPhoto)

        if not self.is_valid():
            return self.no_query_found()

        return sqs


class CatCuratorAlbumEditForm(forms.Form):
    album = forms.ModelChoiceField(queryset=CatAlbum.objects.all())
    title = forms.CharField(max_length=255, required=True)
    subtitle = forms.CharField(max_length=255, required=False)


class CatCuratorAlbumAddForm(forms.ModelForm):
    class Meta:
        model = CatAlbum
        fields = ('title', 'subtitle')


class CatCuratorPhotoUploadForm(forms.Form):
    id = forms.CharField(max_length=100)
    title = forms.CharField(max_length=255, required=False)
    creators = forms.CharField(max_length=255, required=False)
    imageUrl = forms.CharField()
    institution = forms.CharField(max_length=255, required=False)
    urlToRecord = forms.CharField(max_length=1023, required=False)
    identifyingNumber = forms.CharField(max_length=255)
    flip = forms.BooleanField(required=False)
    invert = forms.BooleanField(required=False)
    stereo = forms.BooleanField(required=False)
    rotated = forms.FloatField(min_value=0, max_value=270, required=False)