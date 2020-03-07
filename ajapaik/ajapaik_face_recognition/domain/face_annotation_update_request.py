from django.http import QueryDict

from ajapaik.ajapaik_object_recognition import object_annotation_utils
from ajapaik.ajapaik_object_recognition.domain.detection_rectangle import get_if_key_present
from ajapaik.ajapaik_object_recognition.object_annotation_utils import parse_age_parameter, parse_gender_parameter


class FaceAnnotationUpdateRequest:
    def __init__(self, parameters: QueryDict, annotation_id: int, user_id: int):
        age_guess = get_if_key_present(parameters, 'ageGroup')
        gender_guess = get_if_key_present(parameters, 'gender')

        self.annotation_id = annotation_id

        self.new_subject_id = object_annotation_utils.parse_parameter(parameters['newSubjectId'])
        self.new_age_guess = age_guess is not None and parse_age_parameter(age_guess)
        self.new_gender_guess = gender_guess is not None and parse_gender_parameter(gender_guess)

        self.user_id = user_id
