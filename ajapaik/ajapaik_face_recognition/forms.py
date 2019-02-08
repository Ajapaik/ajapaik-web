import autocomplete_light
from django import forms
from django.utils.translation import ugettext_lazy as _

from ajapaik.ajapaik.models import Photo, Album
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle, \
    FaceRecognitionUserGuess, FaceRecognitionRectangleFeedback


class FaceRecognitionAddPersonForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FaceRecognitionAddPersonForm, self).__init__(*args, **kwargs)
        self.fields['gender'].widget = forms.RadioSelect(choices=Album.GENDER_CHOICES)

    class Meta:
        model = Album
        fields = ('name', 'date_of_birth', 'gender', 'is_public_figure')


class FaceRecognitionGuessForm(autocomplete_light.ModelForm):
    subject_album = autocomplete_light.ModelChoiceField('PublicAlbumAutocomplete', label=_('Subject'), required=True)
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
    x1 = forms.IntegerField()
    y1 = forms.IntegerField()
    x2 = forms.IntegerField()
    y2 = forms.IntegerField()
    seen_width = forms.IntegerField()
    seen_height = forms.IntegerField()
