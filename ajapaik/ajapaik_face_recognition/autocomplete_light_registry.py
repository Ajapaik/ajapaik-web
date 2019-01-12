import autocomplete_light.shortcuts as al
from autocomplete_light import AutocompleteModelBase

from ajapaik.ajapaik_face_recognition.models import FaceRecognitionSubject


class FaceRecognitionSubjectAutocomplete(AutocompleteModelBase):
    model = FaceRecognitionSubject
    name = 'FaceRecognitionSubjectAutocomplete'
    search_fields = ['pk', 'name']
    limit_choices = 10
    attrs = {
        'data-autocomplete-minimum-characters': 3,
    }
    widget_attrs = {
        'data-widget-maximum-values': 4,
        'class': 'modern-style',
    }
    add_another_url_name = 'face_recognition_add_subject'


al.register(FaceRecognitionSubjectAutocomplete)
