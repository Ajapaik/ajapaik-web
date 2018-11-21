import autocomplete_light
from django import forms
from django.utils.translation import ugettext_lazy as _

from project.ajapaik.models import FaceRecognitionUserGuess, Photo, FaceRecognitionRectangleFeedback, \
    FaceRecognitionSubject


class FaceRecognitionAddSubjectForm(forms.ModelForm):
    class Meta:
        model = FaceRecognitionSubject
        fields = ('name', 'date_of_birth', 'gender')


class FaceRecognitionGuessForm(autocomplete_light.ModelForm):
    subject = autocomplete_light.ModelChoiceField('FaceRecognitionSubjectAutocomplete', label=_('Subject'),
                                                  required=True)

    class Meta:
        model = FaceRecognitionUserGuess
        fields = ('subject',)


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
