from django.http import QueryDict

from ajapaik.ajapaik_object_recognition import object_annotation_utils
from ajapaik.ajapaik_object_recognition.domain.detection_rectangle import get_if_key_present
from ajapaik.ajapaik_object_recognition.object_annotation_utils import parse_age_parameter, parse_gender_parameter


class FaceAnnotationUpdateRequest:
    def __init__(self, parameters: QueryDict, annotation_id: int, user_id: int):
        age_suggestion = get_if_key_present(parameters, 'ageGroup')
        gender_suggestion = get_if_key_present(parameters, 'gender')

        self.annotation_id = annotation_id

        self.new_subject_id = object_annotation_utils.parse_parameter(parameters['newSubjectId'])
        self.new_age_suggestion = age_suggestion is not None and parse_age_parameter(age_suggestion)
        self.new_gender_suggestion = gender_suggestion is not None and parse_gender_parameter(gender_suggestion)

        self.user_id = user_id
