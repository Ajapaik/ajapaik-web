from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from ajapaik.ajapaik.models import Licence, Photo, Album


class UserPhotoUploadForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserPhotoUploadForm, self).__init__(*args, **kwargs)
        self.fields['licence'].queryset = Licence.objects.filter(is_public=True)

    class Meta:
        model = Photo
        fields = ('image', 'description', 'uploader_is_author', 'author', 'licence')
        labels = {
            'image': _('Picture file'),
            'description': _('Description'),
            'uploader_is_author': _('I am the author'),
            'author': _('Author'),
            'licence': _('Licence or status of copyright')
        }
        help_texts = {
            'image': _('Accepted formats are .png or .jpg files'),
            'description': _('Add a short description of the picture'),
            'author': _('Author of the picture (photographer, painter)'),
            'licence': _(
                '''Please select a licence to let other people know if and how they can reuse the material you upload.
                \n\nIf you are the author, you can choose the licence (we recommend using open Creative Commons
                 licences). If someone else created the work, you need to use the same licence and rights holder that it
                 currently has.\n\nCurrently we are also accepting content with unclear copyright status,
                please choose ‘Copyright not evaluated’ then.''')
        }
        widgets = {
            'description': forms.Textarea(
                attrs={'rows': 1, 'cols': 40, 'placeholder': _('Description of the picture')}),
            'author': forms.TextInput(attrs={'placeholder': _('Author name')}),
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
        self.fields['location'].label = _('Location')
        self.fields['location'].help_text = _('If this album is tied to a certain location, specify here')
        self.fields['lat'].widget = forms.HiddenInput()
        self.fields['lon'].widget = forms.HiddenInput()
        self.fields['atype'].label = _('Album type')
        self.fields['atype'].choices = [(Album.CURATED, _('Anything else')), (Album.PERSON, _('Person'))]
        self.fields['name'].label = _('Name')
        self.fields['description'].label = _('Description')
        self.fields['is_public'].label = _('Is public')
        self.fields['open'].label = _('Is open')
