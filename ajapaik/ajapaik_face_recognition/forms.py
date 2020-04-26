from django import forms
from django.utils.translation import ugettext_lazy as _

from dal import autocomplete

from ajapaik.ajapaik.models import Photo, Album
from ajapaik.ajapaik.autocomplete import autocomplete_form_factory
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle, \
    FaceRecognitionUserGuess, FaceRecognitionRectangleFeedback


class FaceRecognitionAddPersonForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FaceRecognitionAddPersonForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = _('Subject name')
        self.fields['gender'].widget = forms.RadioSelect(choices=Album.GENDER_CHOICES)
        self.fields['is_public_figure'].label = _('Is public figure')

    class Meta:
        model = Album
        fields = ('name', 'gender', 'is_public_figure')


class FaceRecognitionGuessForm(forms.ModelForm):
    subject_album = forms.ModelChoiceField(
        queryset=Album.objects.all(),
        required=True,
        widget=autocomplete.ModelSelect2(url='subject-album-autocomplete')
    )
    rectangle = forms.ModelChoiceField(queryset=FaceRecognitionRectangle.objects.all(), widget=forms.HiddenInput())

    class Meta:
        model = FaceRecognitionUserGuess
        fields = ('subject_album', 'rectangle')


class FaceRecognitionRectangleFeedbackForm(forms.ModelForm):
    class Meta:
        model = FaceRecognitionRectangleFeedback
        fields = ('rectangle', 'is_correct')


class FaceRecognitionRectangleSubmitForm(forms.Form):
    photo = forms.ModelChoiceField(queryset=Photo.objects.filter(rephoto_of_id__isnull=True))
    x1 = forms.IntegerField(min_value=1)
    y1 = forms.IntegerField(min_value=1)
    x2 = forms.IntegerField(min_value=1)
    y2 = forms.IntegerField(min_value=1)
    seen_width = forms.IntegerField(min_value=1)
    seen_height = forms.IntegerField(min_value=1)
