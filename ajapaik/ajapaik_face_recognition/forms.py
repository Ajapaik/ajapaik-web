from dal import autocomplete
from django import forms
from django.utils.translation import gettext_lazy as _

from ajapaik.ajapaik.models import Album
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle, \
    FaceRecognitionUserSuggestion


class FaceRecognitionAddPersonForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FaceRecognitionAddPersonForm, self).__init__(*args, **kwargs)
        self.fields['gender'].widget = forms.RadioSelect(choices=[(1, _('Male')), (0, _('Female'))])

    class Meta:
        model = Album
        fields = ('name', 'date_of_birth', 'gender', 'is_public_figure', 'description')
        labels = {
            'name': _('Person name'),
            'date_of_birth': _('Date of birth'),
            'gender': _('Gender'),
            'is_public_figure': _('Is public figure'),
            'description': _('Description')
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': _('Firstname Lastname')}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 1, 'cols': 40, 'placeholder': _(
                'Additional remarks about the person (other names etc)')}),
        }


class FaceRecognitionSuggestionForm(forms.ModelForm):
    subject_album = forms.ModelChoiceField(
        queryset=Album.objects.all(),
        required=True,
        widget=autocomplete.ModelSelect2(url='subject-album-autocomplete')
    )
    rectangle = forms.ModelChoiceField(queryset=FaceRecognitionRectangle.objects.all(), widget=forms.HiddenInput())

    class Meta:
        model = FaceRecognitionUserSuggestion
        fields = ('subject_album', 'rectangle')
